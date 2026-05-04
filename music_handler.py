"""
Music Handler - v2.1 (Stabilny YouTube)
Multi-format fallback + Invidious API
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

YOUTUBE_FORMATS = [
    {"ext": "m4a", "acodec": "mp4a"},
    {"ext": "webm", "acodec": "opus"},
    {"ext": "mp4", "acodec": "mp4a"},
    {"ext": "null", "acodec": "aac"},
]

INVIDIOUS_INSTANCES = [
    "https://invidious.jingl.xyz",
    "https://invidious.protondll.xyz",
    "https://invidious.stv2090449.com",
]


def is_youtube_url(url):
    return "youtube.com" in url or "youtu.be" in url


def is_spotify_url(url):
    return "spotify.com" in url


def is_spotify_track(url):
    return is_spotify_url(url) and "/track/" in url


def get_ydl_opts():
    """Podstawowe opcje yt-dlp"""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
    }
    if os.path.exists(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
    return opts


def get_best_audio_url(formats):
    """Znajdź najlepszy audio URL z formats"""
    for target in YOUTUBE_FORMATS:
        for f in reversed(formats):
            ext = f.get("ext", "")
            acodec = f.get("acodec", "")
            url = f.get("url")
            if url and (ext == target["ext"] or acodec == target["acodec"]):
                logger.debug(f"[get_best_audio] Found: {ext} {acodec}")
                return url
    return None


async def get_invidious_url(video_id):
    """Pobierz URL z Invidious API"""
    for instance in INVIDIOUS_INSTANCES:
        try:
            resp = requests.get(f"{instance}/api/v1/videos/{video_id}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for f in data.get("adaptiveFormats", []) + data.get("formatStreams", []):
                    if f.get("type", "").startswith("audio"):
                        url = f.get("url")
                        if url:
                            logger.info(f"[Invidious] OK: {instance}")
                            return url
        except Exception as e:
            logger.warning(f"[Invidious] {instance}: {e}")
    return None


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title", "Utwór")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        video_id = None
        
        if "youtube.com/watch" in url or "youtu.be/" in url:
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            else:
                video_id = url.split("/")[-1].split("?")[0]
        
        ydl = yt_dlp.YoutubeDL(get_ydl_opts())
        
        try:
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            
            if not data or not isinstance(data, dict):
                return await cls.from_url_fallback(url, video_id, loop)
            
            title = data.get("title", "Unknown")
            audio_url = data.get("url")
            
            if not audio_url and "formats" in data:
                audio_url = get_best_audio_url(data["formats"])
            
            if audio_url:
                logger.info(f"[from_url] OK: {title[:30]}")
                return cls(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS), data=data)
            
            logger.warning(f"[from_url] Brak URL, próbuję Invidious...")
            
        except Exception as e:
            logger.warning(f"[from_url] yt-dlp failed: {e}")
        
        if video_id:
            invidious_url = await get_invidious_url(video_id)
            if invidious_url:
                data = {"title": title, "url": url, "id": video_id}
                logger.info(f"[from_url] Invidious OK: {title[:30]}")
                return cls(discord.FFmpegPCMAudio(invidious_url, **FFMPEG_OPTIONS), data=data)
        
        return await cls.from_url_fallback(url, video_id, loop)

    @classmethod
    async def from_url_fallback(cls, url, video_id, loop):
        """Fallback - szukaj na YouTube"""
        import requests
        
        query = url
        if is_youtube_url(url) and video_id:
            query = video_id
        elif is_spotify_url(url):
            query = url.split("/")[-1].split("?")[0]
        
        try:
            ydl = yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "default_search": "ytsearch1"})
            data = await loop.run_in_executor(
                None, lambda: ydl.extract_info(f"ytsearch1:{query}", download=False)
            )
            if data and "entries" in data and data["entries"]:
                entry = data["entries"][0]
                audio_url = entry.get("url")
                if not audio_url and "id" in entry:
                    audio_url = f"https://www.youtube.com/watch?v={entry['id']}"
                if audio_url:
                    logger.info(f"[from_url] Fallback OK: {entry.get('title', '?')[:30]}")
                    return cls(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS), data=entry)
        except Exception as e:
            logger.error(f"[from_url] Fallback failed: {e}")
        
        return None


async def get_track_info(url, *, loop=None):
    """Pobierz info o utworze"""
    loop = loop or asyncio.get_event_loop()
    ydl_opts = get_ydl_opts()
    
    if is_spotify_track(url):
        try:
            resp = requests.get("https://open.spotify.com/oembed", params={"url": url}, timeout=5)
            if resp.status_code == 200:
                title = resp.json().get("title", "")
                if title:
                    logger.info(f"[get_info] Spotify: {title}")
                    ydl = yt_dlp.YoutubeDL(ydl_opts)
                    data = await loop.run_in_executor(
                        None, lambda: ydl.extract_info(f"ytsearch1:{title}", download=False)
                    )
                    return process_info_data(data)
        except Exception as e:
            logger.warning(f"[get_info] Spotify failed: {e}")
        return {"entries": []}
    
    try:
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        return process_info_data(data)
    except Exception as e:
        logger.warning(f"[get_info] Błąd: {e}")
        if is_youtube_url(url) and "playlist" not in url:
            video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
            return {"entries": [{"url": url, "title": video_id}]}
        return {"entries": []}


def process_info_data(data):
    """Przetwórz dane z yt-dlp"""
    if not data:
        return {"entries": []}
    
    if "entries" in data:
        entries = [e for e in data["entries"] if e is not None]
        for e in entries:
            if isinstance(e, dict) and "id" in e and "url" not in e:
                e["url"] = f"https://www.youtube.com/watch?v={e['id']}"
        return {"entries": entries}
    
    if isinstance(data, dict):
        if "id" in data and "url" not in data:
            data["url"] = f"https://www.youtube.com/watch?v={data['id']}"
        return {"entries": [data]}
    
    return {"entries": []}