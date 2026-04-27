import discord
import asyncio
import yt_dlp
import os
import logging

logger = logging.getLogger('MusicBot')

# Całkowicie wyłączamy ścieżkę do ciasteczek
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

def get_ydl_options(for_playlist=False):
    """Opcje yt-dlp z web_embedded client (stabilny na VPS) + timeout."""
    return {
        "format": "bestaudio/best",
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "nocheckcertificate": True,
        "ignoreerrors": True if for_playlist else False,
        "extract_flat": False,
        "socket_timeout": 30,  # Socket timeout 30s
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "extractor_args": {
            "youtube": {
                "player_client": ["web_embedded", "tv_embedded", "android"],
                "skip_unavailable_videos": True
            }
        },
    }

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
    async def from_url(cls, url, *, loop=None, stream=True):
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
        
        opts = get_ydl_search_options()
        logger.info(f"[get_info] Using search options: extract_flat={opts.get('extract_flat')}, player_client={opts.get('extractor_args', {}).get('youtube', {}).get('player_client')}")
        
        try:
            logger.info(f"[get_info] Attempting primary extract_info...")
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            logger.info(f"[get_info PRIMARY SUCCESS] Got data with entries count: {len(data.get('entries', [])) if data else 0}")
            if data:
                return data
            logger.warning(f"[get_info] Primary returned None, using empty dict")
            return {"entries": []}
            
        except Exception as e:
            logger.warning(f"[get_info EXCEPTION] {type(e).__name__}: {str(e)[:80]}")
            # Fallback: szukaj na YouTube zamiast dawać up
            query = url.split('/')[-1] if '/' in url else url
            logger.info(f"[get_info FALLBACK START] Query: {query[:50]}")
            
            try:
                search_url = f"ytsearch:{query}"
                logger.info(f"[get_info FALLBACK] Searching: {search_url}")
                
                fallback_opts = get_ydl_search_options()
                # Nie zmieniaj extract_flat - chcemy entries!
                logger.info(f"[get_info FALLBACK] Opts: extract_flat={fallback_opts.get('extract_flat')}, playlistend={fallback_opts.get('playlistend')}")
                
                with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                    data = await loop.run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))
                
                logger.info(f"[get_info FALLBACK SUCCESS] Got data with entries: {len(data.get('entries', [])) if data else 0}")
                return data if data else {"entries": []}
                
            except Exception as e2:
                logger.error(f"[get_info FALLBACK FAILED] {type(e2).__name__}: {str(e2)[:80]}")
                return {"entries": []}