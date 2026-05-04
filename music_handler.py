"""
Music Handler - v2.0 (Prosty & Zoptymalizowany)
Obsługa YouTube/Spotify + Audio Streaming
"""

import discord
import asyncio
import yt_dlp
import os
import logging
import subprocess
import requests

logger = logging.getLogger('MusicBot')

COOKIES_PATH = "config/cookies.txt"

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 30000000",
    "options": "-vn",
    "stderr": subprocess.DEVNULL,
}


def is_youtube_url(url):
    return "youtube.com" in url or "youtu.be" in url


def is_spotify_url(url):
    return "spotify.com" in url


def is_spotify_track(url):
    return is_spotify_url(url) and "/track/" in url


def get_ydl_opts():
    """Proste opcje yt-dlp - używamy default klienta"""
    opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "extractor_args": {
            "youtube": {"player_client": ["web", "default"]}
        }
    }
    if os.path.exists(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
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
        ydl_opts = get_ydl_opts()
        
        try:
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=not stream))
        except Exception as e:
            logger.warning(f"[from_url] Błąd: {e}, próbuję wyszukiwanie...")
            # Fallback: szukaj na YouTube
            query = url.split("/")[-1].split("?")[0] if "/" in url else url
            try:
                ydl2 = yt_dlp.YoutubeDL(ydl_opts)
                data = await loop.run_in_executor(
                    None, lambda: ydl2.extract_info(f"ytsearch1:{query}", download=False)
                )
            except Exception as e2:
                logger.error(f"[from_url] Fallback failed: {e2}")
                return None
        
        # Parsuj wynik
        if not data:
            logger.warning("[from_url] Brak danych")
            return None
        
        # Jeśli to playlista z entries
        if "entries" in data:
            entries = [e for e in data["entries"] if e is not None]
            if not entries:
                logger.warning("[from_url] Brak valid entries")
                return None
            data = entries[0]
        
        if not data or not isinstance(data, dict):
            logger.warning(f"[from_url] Nieprawidłowe dane: {type(data)}")
            return None
        
        # Konwertuj id -> url jeśli potrzeba
        if "id" in data and "url" not in data:
            data["url"] = f"https://www.youtube.com/watch?v={data['id']}"
        
        audio_url = data.get("url")
        if not audio_url:
            logger.warning("[from_url] Brak URL w danych")
            return None
        
        logger.info(f"[from_url] Odtwarzam: {data.get('title', 'unknown')}")
        return cls(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS), data=data)


async def get_track_info(url, *, loop=None):
    """Pobierz info o utworze/playlist"""
    loop = loop or asyncio.get_event_loop()
    ydl_opts = get_ydl_opts()
    
    # Spotify -> YouTube search przez oEmbed
    if is_spotify_track(url):
        try:
            import requests
            resp = requests.get("https://open.spotify.com/oembed", params={"url": url}, timeout=5)
            if resp.status_code == 200:
                title = resp.json().get("title", "")
                if title:
                    logger.info(f"[get_info] Spotify title: {title}")
                    ydl = yt_dlp.YoutubeDL(ydl_opts)
                    data = await loop.run_in_executor(
                        None, lambda: ydl.extract_info(f"ytsearch1:{title}", download=False)
                    )
                    return process_info_data(data)
        except Exception as e:
            logger.warning(f"[get_info] Spotify failed: {e}")
        return {"entries": []}
    
    # YouTube direct
    try:
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        return process_info_data(data)
    except Exception as e:
        logger.warning(f"[get_info] Błąd: {e}")
        # Fallback: syntetyczny wpis dla YouTube URL
        if is_youtube_url(url) and "playlist" not in url:
            video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
            return {"entries": [{"url": url, "title": video_id}]}
        return {"entries": []}


def process_info_data(data):
    """Przetwórz dane z yt-dlp - konwertuj id -> url"""
    if not data:
        return {"entries": []}
    
    if "entries" in data:
        entries = [e for e in data["entries"] if e is not None]
        for e in entries:
            if isinstance(e, dict) and "id" in e and "url" not in e:
                e["url"] = f"https://www.youtube.com/watch?v={e['id']}"
        return {"entries": entries}
    
    # Single video
    if isinstance(data, dict):
        if "id" in data and "url" not in data:
            data["url"] = f"https://www.youtube.com/watch?v={data['id']}"
        return {"entries": [data]}
    
    return {"entries": []}