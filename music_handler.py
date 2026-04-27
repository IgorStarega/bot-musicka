import discord
import asyncio
import yt_dlp
import os
import logging
import requests

logger = logging.getLogger('MusicBot')

# Ścieżka do ciasteczek YouTube (eksportowane z przeglądarki)
COOKIES_PATH = "config/cookies.txt"

# Opcje dla FFmpeg
FFMPEG_OPTIONS = {
    "before_options": (
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
        "-timeout 30000000"
    ),
    "options": "-vn -dn -sn -ignore_unknown -probesize 32k -analyzeduration 0 -threads 1",
}

RADIO_FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 30000000",
    "options": "-vn",
}

# --- FUNKCJE POMOCNICZE (Przywrócone dla main.py) ---

def is_youtube_url(url):
    return "youtube.com" in url or "youtu.be" in url

def is_youtube_playlist(url):
    return is_youtube_url(url) and ("playlist?list=" in url or "&list=" in url)

def is_spotify_url(url):
    return "spotify.com" in url

def is_spotify_playlist(url):
    return is_spotify_url(url) and "/playlist/" in url

def is_spotify_track(url):
    return is_spotify_url(url) and "/track/" in url

# --- KONFIGURACJA YT-DLP ---

def _get_spotify_title(url):
    """Pobierz tytuł utworu/playlisty Spotify przez oEmbed API (bez autoryzacji)."""
    try:
        resp = requests.get(
            "https://open.spotify.com/oembed",
            params={"url": url},
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json().get("title", "")
    except Exception as e:
        logger.warning(f"[Spotify oEmbed] {type(e).__name__}: {e}")
    return ""

def get_ydl_options(for_playlist=False):
    """Opcje yt-dlp z ios+web_embedded client (stabilny na VPS) + cookies + timeout."""
    opts = {
        "format": "bestaudio/best",
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "nocheckcertificate": True,
        "ignoreerrors": True if for_playlist else False,
        "extract_flat": False,
        "socket_timeout": 30,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "extractor_args": {
            "youtube": {
                "player_client": ["ios", "web_embedded", "tv_embedded"],
                "skip_unavailable_videos": True
            }
        },
    }
    if os.path.exists(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
    return opts

def get_ydl_search_options():
    """Opcje dla wyszukiwania - musi zwrócić entries zamiast single track"""
    opts = get_ydl_options(for_playlist=True)
    # Nie używaj extract_flat dla ytsearch - chcemy entries
    opts["extract_flat"] = False
    # Zwiększ limit wyników
    opts["playlistend"] = 5
    return opts

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title", "Utwór")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True, title_hint=None):
        loop = loop or asyncio.get_event_loop()
        logger.info(f"[from_url START] URL: {url[:60]}, stream={stream}")
        
        if url.startswith("ytsearch:") or not is_youtube_url(url):
            opts = get_ydl_search_options()
            logger.info(f"[from_url] Using SEARCH options")
        else:
            opts = get_ydl_options()
            logger.info(f"[from_url] Using standard options")

        try:
            logger.info(f"[from_url] Attempting extract_info...")
            ydl = yt_dlp.YoutubeDL(opts)
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=not stream))
            logger.info(f"[from_url SUCCESS] Got data, has entries: {'entries' in data if data else False}")
        except Exception as e:
            logger.warning(f"[from_url EXCEPTION] {type(e).__name__}: {str(e)[:80]}")
            # Fallback: spróbuj wyszukać na YouTube
            # Użyj title_hint jeśli dostępny, w przeciwnym razie wyciągnij sensowny query z URL
            if title_hint:
                query = title_hint
            elif is_youtube_url(url):
                # Dla YouTube URL bez tytułu, ekstrahuj video_id obsługując oba formaty
                if "v=" in url:
                    query = url.split("v=")[-1].split("&")[0]
                elif "youtu.be/" in url:
                    query = url.split("youtu.be/")[-1].split("?")[0]
                else:
                    query = url.split("/")[-1].split("?")[0]
            else:
                query = url.split('/')[-1] if '/' in url else url
            logger.info(f"[from_url FALLBACK] Searching for: {query[:50]}")
            
            try:
                search_opts = get_ydl_search_options()
                logger.info(f"[from_url FALLBACK] Using search opts")
                ydl_search = yt_dlp.YoutubeDL(search_opts)
                data = await loop.run_in_executor(None, lambda: ydl_search.extract_info(f"ytsearch:{query}", download=False))
                logger.info(f"[from_url FALLBACK SUCCESS] Got search results")
            except Exception as e2:
                logger.error(f"[from_url FALLBACK FAILED] {type(e2).__name__}: {str(e2)[:80]}")
                return None

        if data is None or not data:
            logger.warning(f"[from_url] Data is None or empty")
            return None

        if "entries" in data:
            if not data["entries"]:
                return None
            data = data["entries"][0]

        filename = data.get("url")
        if not filename:
            return None
            
        logger.info(f"✅ Przygotowano: {data.get('title')}")
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

    @classmethod
    async def get_info(cls, url, *, loop=None):
        """Pobierz info o URL - zwraca dict z entries lub empty dict"""
        loop = loop or asyncio.get_event_loop()
        logger.info(f"[get_info START] URL: {url[:60]}")

        # Spotify: DRM-protected, redirect do wyszukiwania YouTube przez oEmbed title
        if is_spotify_url(url):
            logger.info(f"[get_info] Spotify URL - pobieranie tytułu przez oEmbed...")
            title = await loop.run_in_executor(None, _get_spotify_title, url)
            if not title:
                # Fallback: użyj ID traka/playlisty jako query
                title = url.split("/")[-1].split("?")[0]
                logger.warning(f"[get_info] oEmbed nieudane, szukam po ID: {title}")
            else:
                logger.info(f"[get_info] oEmbed title: {title[:50]}")
            search_url = f"ytsearch:{title}"
            opts = get_ydl_search_options()
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    data = await loop.run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))
                if data and data.get("entries"):
                    logger.info(f"[get_info] Spotify→YT sukces: {len(data['entries'])} wpisów")
                    return data
            except Exception as e:
                logger.error(f"[get_info] Spotify→YT search FAILED: {type(e).__name__}: {str(e)[:80]}")
            return {"entries": []}

        opts = get_ydl_search_options()
        logger.info(f"[get_info] Using search options: extract_flat={opts.get('extract_flat')}, player_client={opts.get('extractor_args', {}).get('youtube', {}).get('player_client')}")

        try:
            logger.info(f"[get_info] Attempting primary extract_info...")
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            logger.info(f"[get_info PRIMARY SUCCESS] Got data with entries count: {len(data.get('entries', [])) if data else 0}")
            # Sprawdź czy data zawiera użyteczne wpisy
            if data and (data.get("entries") or "url" in data or "formats" in data):
                return data
            logger.warning(f"[get_info] Primary zwróciło puste dane, próbuję fallback")
        except Exception as e:
            logger.warning(f"[get_info EXCEPTION] {type(e).__name__}: {str(e)[:80]}")

        # Dla bezpośredniego URL YouTube (nie playlist) - zwróć syntetyczny wpis,
        # żeby from_url() mógł spróbować z cookies
        if is_youtube_url(url) and not is_youtube_playlist(url) and not url.startswith("ytsearch:"):
            logger.info(f"[get_info] Zwracam syntetyczny wpis dla YouTube URL")
            # Obsługa youtube.com/watch?v=ID i youtu.be/ID
            if "v=" in url:
                video_id = url.split("v=")[-1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[-1].split("?")[0]
            else:
                video_id = url.split("/")[-1].split("?")[0]
            return {"entries": [{"url": url, "title": f"Utwór [{video_id}]"}]}

        # Ogólny fallback: szukaj na YouTube
        query = url.split('/')[-1].split('?')[0] if '/' in url else url
        logger.info(f"[get_info FALLBACK START] Query: {query[:50]}")

        try:
            search_url = f"ytsearch:{query}"
            logger.info(f"[get_info FALLBACK] Searching: {search_url}")

            fallback_opts = get_ydl_search_options()
            logger.info(f"[get_info FALLBACK] Opts: extract_flat={fallback_opts.get('extract_flat')}, playlistend={fallback_opts.get('playlistend')}")

            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))

            logger.info(f"[get_info FALLBACK SUCCESS] Got data with entries: {len(data.get('entries', [])) if data else 0}")
            return data if data else {"entries": []}

        except Exception as e2:
            logger.error(f"[get_info FALLBACK FAILED] {type(e2).__name__}: {str(e2)[:80]}")
            return {"entries": []}