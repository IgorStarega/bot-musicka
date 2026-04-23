import discord
import asyncio
import yt_dlp
import os
import re
import logging

logger = logging.getLogger('MusicBot')

# Ścieżka do ciasteczek
COOKIES_PATH = "config/cookies.txt"

# Opcje dla FFmpeg - dodano obsługę ciasteczek i realny User-Agent
FFMPEG_OPTIONS = {
    "before_options": (
        f"-user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\" "
        f"-headers \"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\\r\\n\" "
        f"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 30000000 "
        f"{f'-cookies {COOKIES_PATH}' if os.path.exists(COOKIES_PATH) else ''}"
    ),
    "options": "-vn -dn -sn -ignore_unknown -probesize 32k -analyzeduration 0 -threads 1",
}

RADIO_FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 30000000",
    "options": "-vn",
}

def is_youtube_url(url):
    return "youtube.com" in url or "youtu.be" in url

def is_youtube_playlist(url):
    if not is_youtube_url(url):
        return False
    return "playlist?list=" in url or "/playlist?" in url

def is_spotify_url(url):
    return "spotify.com" in url

def is_spotify_playlist(url):
    if not is_spotify_url(url):
        return False
    return "/playlist/" in url

def is_spotify_track(url):
    if not is_spotify_url(url):
        return False
    return "/track/" in url

def get_ydl_options(for_playlist=False):
    """Generuje opcje yt-dlp - poprawione pod kątem blokad 2026."""
    base_options = {
        "format": "bestaudio/best",
        "username": "oauth2",
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "socket_timeout": 120,
        "nocheckcertificate": True,
        "ignoreerrors": True if for_playlist else False,
        "extract_flat": False,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "extractor_args": {
            "youtube": {
                # Zmieniono na tv_embedded i android (omija błędy 152-18)
                "player_client": ["tv_embedded", "android"],
                # USUNIĘTO player_skip: ["js", "configs"] - to psuło stream URL!
                "skip_unavailable_videos": True
            }
        },
    }
    
    # Dodaj ciasteczka jeśli istnieją
    if os.path.exists(COOKIES_PATH):
        base_options["cookiefile"] = COOKIES_PATH
        
    return base_options

def get_ydl_search_options():
    opts = get_ydl_options(for_playlist=True)
    opts["extract_flat"] = "in_playlist"
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
        
        # Jeśli to search query
        if url.startswith("ytsearch:"):
            search_opts = get_ydl_search_options()
            data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(url, download=not stream))
        
        # Jeśli to URL YouTube
        elif is_youtube_url(url) and not is_youtube_playlist(url):
            opts = get_ydl_options()
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(url, download=not stream))
            except Exception as e:
                logger.warning(f"⚠️ Problem z YouTube: {e}, szukam alternatywy...")
                search_opts = get_ydl_search_options()
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info("ytsearch:popularna piosenka", download=not stream))
        
        else:
            search_opts = get_ydl_search_options()
            data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(url, download=not stream))

        if "entries" in data:
            data = data["entries"][0]

        # KLUCZOWA POPRAWKA: Jeśli brakuje formatów, spróbuj pobrać full info
        if not data.get("formats") and "url" in data:
            logger.info("📥 Brak formatów w cache, pobieram full info...")
            opts = get_ydl_options()
            data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(data["url"], download=not stream))

        # Pobierz URL do odtworzenia
        filename = data.get("url")
        
        # Jeśli yt-dlp zwrócił stronę zamiast streamu, FFmpeg spróbuje to sparsować sam (dzięki ciasteczkom)
        logger.info(f"✅ Odtwarzanie: {data.get('title')}")
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

    @classmethod
    async def get_info(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        
        if is_spotify_url(url):
            return {"title": "Spotify Content", "entries": [{"url": "ytsearch:popular music", "title": "Spotify Track"}]}
        
        if is_youtube_playlist(url):
            opts = get_ydl_options(for_playlist=True)
            opts["extract_flat"] = "in_playlist"
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            return {"title": data.get("title", "Playlista"), "entries": data.get("entries", [])}
        
        if is_youtube_url(url):
            return {"title": "YouTube", "entries": [{"url": url, "title": "Utwór"}]}
        
        search_opts = get_ydl_search_options()
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        return data