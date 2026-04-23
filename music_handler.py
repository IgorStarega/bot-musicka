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
    """Czyste opcje pod OAuth2."""
    return {
        "format": "bestaudio/best",
        "username": "oauth2",
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "nocheckcertificate": True,
        "ignoreerrors": True if for_playlist else False,
        "extract_flat": False,
        "extractor_args": {
            "youtube": {
                "player_client": ["tv_embedded"],
                "skip_unavailable_videos": True
            }
        },
    }

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
        
        if url.startswith("ytsearch:") or not is_youtube_url(url):
            opts = get_ydl_search_options()
        else:
            opts = get_ydl_options()

        try:
            ydl = yt_dlp.YoutubeDL(opts)
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=not stream))
        except Exception as e:
            logger.error(f"❌ Błąd yt-dlp: {e}")
            return None

        if data is None:
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
        loop = loop or asyncio.get_event_loop()
        opts = get_ydl_search_options()
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            return data
        except:
            return None