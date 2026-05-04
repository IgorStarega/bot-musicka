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
    """Op yt-dlp - bez format, tylko info"""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
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
        
        # Dla wyszukiwania użyj innych opcji
        search_opts = {
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30,
            "default_search": "ytsearch1",
        }
        
        try:
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            # Próbuj bez download - weź info
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            
            if data and isinstance(data, dict):
                # Szukaj URL w różnych miejscach
                audio_url = data.get("url")
                
                # Sprawdź formats
                if not audio_url and "formats" in data:
                    for f in reversed(data["formats"]):
                        if f.get("url") and f.get("ext") in ("m4a", "mp4", "webm", "null"):
                            audio_url = f["url"]
                            break
                
                # Fallback - zbuduj z ID
                if not audio_url and "id" in data:
                    video_id = data["id"]
                    # YouTube live stream URL
                    audio_url = f"https://www.youtube.com/watch?v={video_id}"
                
                if audio_url:
                    logger.info(f"[from_url] OK: {data.get('title', 'unknown')[:30]}")
                    return cls(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS), data=data)
                else:
                    logger.warning(f"[from_url] Brak URL w danych")
                    return None
            else:
                logger.warning(f"[from_url] Brak danych")
                return None
                
        except Exception as e:
            logger.warning(f"[from_url] Błąd: {e}")
            # Fallback: szukaj na YouTube
            query = url.split("/")[-1].split("?")[0] if "/" in url else url
            try:
                ydl2 = yt_dlp.YoutubeDL(search_opts)
                data = await loop.run_in_executor(
                    None, lambda: ydl2.extract_info(f"ytsearch1:{query}", download=False)
                )
                if data and "entries" in data and data["entries"]:
                    data = data["entries"][0]
                    audio_url = data.get("url")
                    if not audio_url and "id" in data:
                        audio_url = f"https://www.youtube.com/watch?v={data['id']}"
                    if audio_url:
                        logger.info(f"[from_url] Fallback OK: {data.get('title', '?')[:30]}")
                        return cls(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS), data=data)
            except Exception as e2:
                logger.error(f"[from_url] Fallback failed: {e2}")
            return None
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