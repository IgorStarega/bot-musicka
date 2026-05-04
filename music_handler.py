import discord
import asyncio
import yt_dlp
import os
import logging
import subprocess
import requests

logger = logging.getLogger('MusicBot')

# Ścieżka do ciasteczek YouTube (eksportowane z przeglądarki)
COOKIES_PATH = "config/cookies.txt"


class _YtdlpLogger:
    """Przekierowuje WSZYSTKIE komunikaty yt-dlp przez Python logging.

    Wszystkie poziomy (debug/info/warning/error) trafiają do logger.debug(),
    dzięki czemu żadna linia 'ERROR:' lub 'WARNING:' z yt-dlp nie pojawia się
    bezpośrednio w logach Dockera (domyślny poziom to INFO).
    Nasze własne logger.warning/error() nadal działają normalnie.
    """
    def debug(self, msg):
        logger.debug(f"[yt-dlp] {msg}")
    def info(self, msg):
        logger.debug(f"[yt-dlp] {msg}")
    def warning(self, msg):
        logger.debug(f"[yt-dlp] {msg}")
    def error(self, msg):
        logger.debug(f"[yt-dlp] {msg}")

# Opcje dla FFmpeg
# stderr=DEVNULL: FFmpeg outputuje swoje błędy do stderr kontenera (Docker logs),
# co zaśmieca logi nawet gdy błędy są nieistotne. Wyciszamy to całkowicie.
FFMPEG_OPTIONS = {
    "before_options": (
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
        "-timeout 30000000"
    ),
    "options": "-vn -dn -sn -ignore_unknown -probesize 32k -analyzeduration 0 -threads 1",
    "stderr": subprocess.DEVNULL,
}

RADIO_FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 30000000",
    "options": "-vn",
    "stderr": subprocess.DEVNULL,
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
        logger.warning(f"[Spotify oEmbed] HTTP {resp.status_code} dla {url[:60]}...")
    except Exception as e:
        logger.warning(f"[Spotify oEmbed] {type(e).__name__}: {e}")
    return ""

def _extract_youtube_video_id(url):
    """Wyciągnij ID wideo z YouTube URL (watch?v=, youtu.be/, lub ostatni segment)."""
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return url.split("/")[-1].split("?")[0]

def get_ydl_options(for_playlist=False):
    """Opcje yt-dlp z mweb+ios client (lepiej omija bot-detection na VPS) + cookies + timeout."""
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
        "logger": _YtdlpLogger(),
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "extractor_args": {
            "youtube": {
                "player_client": ["mweb", "ios", "web_embedded"],
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
        logger.debug(f"[from_url] URL: {url[:60]}, stream={stream}")
        
        if url.startswith("ytsearch:") or not is_youtube_url(url):
            opts = get_ydl_search_options()
        else:
            opts = get_ydl_options()

        try:
            ydl = yt_dlp.YoutubeDL(opts)
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=not stream))
            logger.debug(f"[from_url] OK, has entries: {'entries' in data if data else False}")
        except Exception as e:
            logger.warning(f"[from_url] {type(e).__name__}: {str(e)[:80]}")
            # Fallback: spróbuj wyszukać na YouTube
            if title_hint:
                query = title_hint
            elif is_youtube_url(url):
                if "v=" in url:
                    query = url.split("v=")[-1].split("&")[0]
                elif "youtu.be/" in url:
                    query = url.split("youtu.be/")[-1].split("?")[0]
                else:
                    query = url.split("/")[-1].split("?")[0]
            else:
                query = url.split('/')[-1] if '/' in url else url
            logger.info(f"[from_url] Fallback search: {query[:50]}")
            
            try:
                search_opts = get_ydl_search_options()
                ydl_search = yt_dlp.YoutubeDL(search_opts)
                data = await loop.run_in_executor(None, lambda: ydl_search.extract_info(f"ytsearch:{query}", download=False))
                logger.debug(f"[from_url] Fallback OK")
            except Exception as e2:
                logger.error(f"[from_url] Fallback FAILED: {type(e2).__name__}: {str(e2)[:80]}")
                return None

        if data is None or not data:
            logger.warning(f"[from_url] Data is None or empty")
            return None

        if "entries" in data:
            if not data["entries"]:
                logger.warning(f"[from_url] No entries found in data")
                return None
            data = data["entries"][0]

        if not isinstance(data, dict):
            logger.warning(f"[from_url] Data is not dict: {type(data)}")
            return None

        filename = data.get("url")
        if not filename:
            logger.warning(f"[from_url] No URL in data: {data.get('title', 'unknown')}")
            return None
            
        logger.info(f"✅ Przygotowano: {data.get('title')}")
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

    @classmethod
    async def get_info(cls, url, *, loop=None):
        """Pobierz info o URL - zwraca dict z entries lub empty dict"""
        loop = loop or asyncio.get_event_loop()
        logger.info(f"[get_info] URL: {url[:60]}")

        # Spotify: DRM-protected, redirect do wyszukiwania YouTube przez oEmbed title
        if is_spotify_url(url):
            logger.info(f"[get_info] Spotify → oEmbed → YouTube search")
            title = await loop.run_in_executor(None, _get_spotify_title, url)
            if not title:
                logger.warning(f"[get_info] Spotify oEmbed API nie zwróciło tytułu - utwór zostanie pominięty. Sprawdź czy link Spotify jest poprawny.")
                return {"entries": []}
            else:
                logger.debug(f"[get_info] oEmbed title: {title[:50]}")
            search_url = f"ytsearch:{title}"
            opts = get_ydl_search_options()
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    data = await loop.run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))
                if data and data.get("entries"):
                    logger.info(f"[get_info] Spotify→YT OK: {len(data['entries'])} wpisów")
                    return data
            except Exception as e:
                logger.error(f"[get_info] Spotify→YT FAILED: {type(e).__name__}: {str(e)[:80]}")
            return {"entries": []}

        opts = get_ydl_search_options()

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            entry_count = len(data.get("entries", [])) if data else 0
            logger.info(f"[get_info] OK, entries: {entry_count}")
            if data and (data.get("entries") or "url" in data or "formats" in data):
                if "entries" not in data:
                    data = {"entries": [data], "title": data.get("title", "")}
                return data
            logger.warning(f"[get_info] Puste dane, próbuję fallback")
        except Exception as e:
            logger.warning(f"[get_info] {type(e).__name__}: {str(e)[:80]}")

        # Dla bezpośredniego URL YouTube (nie playlist) - zwróć syntetyczny wpis
        # Tytuł to samo ID wideo (nie "Utwór [ID]") - dzięki temu fallback ytsearch działa
        if is_youtube_url(url) and not is_youtube_playlist(url) and not url.startswith("ytsearch:"):
            logger.info(f"[get_info] Syntetyczny wpis dla YouTube URL")
            if "v=" in url:
                video_id = url.split("v=")[-1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[-1].split("?")[0]
            else:
                video_id = url.split("/")[-1].split("?")[0]
            return {"entries": [{"url": url, "title": video_id}]}

        # Ogólny fallback: szukaj na YouTube
        query = url.split('/')[-1].split('?')[0] if '/' in url else url
        logger.info(f"[get_info] Fallback search: {query[:50]}")

        try:
            search_url = f"ytsearch:{query}"
            fallback_opts = get_ydl_search_options()
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))
            logger.info(f"[get_info] Fallback OK, entries: {len(data.get('entries', [])) if data else 0}")
            if not data:
                return {"entries": []}
            if "entries" not in data and ("url" in data or "formats" in data):
                data = {"entries": [data], "title": data.get("title", "")}
            return data

        except Exception as e2:
            logger.error(f"[get_info] Fallback FAILED: {type(e2).__name__}: {str(e2)[:80]}")
            return {"entries": []}