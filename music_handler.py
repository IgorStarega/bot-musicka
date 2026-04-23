import discord
import asyncio
import yt_dlp

# Opcje dla FFmpeg - zoptymalizowane pod kątem stabilności i szybkości startu
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 10000000",
    "options": "-vn -dn -sn -ignore_unknown -probesize 32 -analyzeduration 0",
}

# Opcje dla yt-dlp - zoptymalizowane pod kątem playlist i omijania blokad
YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "cookiefile": "cookies.txt",
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "logtostderr": False,
    "no_color": True,
    "youtube_include_dash_manifest": False,
    "youtube_include_hls_manifest": False,
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        
        if "spotify.com" in url:
            url = url.split("?")[0]
            
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=not stream))
            
            if "entries" in data:
                data = data["entries"][0]

            filename = data["url"]
            return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

    @classmethod
    async def get_info(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            return await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))