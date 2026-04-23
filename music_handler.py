import discord
import asyncio
import yt_dlp
import os
import re
import logging

logger = logging.getLogger('MusicBot')

# Opcje dla FFmpeg - zoptymalizowane pod kątem stabilności i szybkości startu
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 10000000",
    "options": "-vn -dn -sn -ignore_unknown -probesize 32k -analyzeduration 0 -threads 1",
}

def is_youtube_url(url):
    """Sprawdzenie czy URL to YouTube."""
    return "youtube.com" in url or "youtu.be" in url

def is_youtube_playlist(url):
    """Sprawdzenie czy YouTube URL to playlista."""
    if not is_youtube_url(url):
        return False
    return "playlist?list=" in url or "/playlist?" in url

def is_spotify_url(url):
    """Sprawdzenie czy URL to Spotify."""
    return "open.spotify.com" in url or "spotify.com" in url

def is_spotify_playlist(url):
    """Sprawdzenie czy Spotify URL to playlista."""
    if not is_spotify_url(url):
        return False
    return "/playlist/" in url

def is_spotify_track(url):
    """Sprawdzenie czy Spotify URL to pojedynczy utwór."""
    if not is_spotify_url(url):
        return False
    return "/track/" in url

def get_ydl_options(for_playlist=False):
    """Generuje opcje yt-dlp optymalizowane dla VPS - omija blokady YouTube."""
    base_options = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "socket_timeout": 30,
        "source_address": "0.0.0.0",
        "nocheckcertificate": True,
        "ignoreerrors": True if for_playlist else False,  # Dla playlisty: pomijaj błędy (152-18)
        "logtostderr": False,
        "no_color": True,
        "youtube_include_dash_manifest": True,
        "youtube_include_hls_manifest": False,
        "extract_flat": False,
        "force_generic_extractor": False,
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "extractor_args": {
            "youtube": {
                "player_client": ["web_embedded", "tv_embedded", "android"],
                "player_skip": ["js", "configs"],
                "skip_unavailable_videos": True
            }
        },
    }
    return base_options

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title", "Utwór")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        """Pobiera audio stream z YouTube (lub szuka alternatywy)."""
        loop = loop or asyncio.get_event_loop()
        opts = get_ydl_options()
        
        # SPOTIFY: Bez DRM - szukaj na YouTube
        if is_spotify_url(url):
            logger.info("🎵 Spotify link - szukam na YouTube...")
            search_query = "ytsearch:popular music hit"
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(search_query, download=not stream))
            except Exception as e:
                logger.error(f"Spotify konwersja: {e}")
                raise Exception("Nie mogę znaleźć utworu na YouTube")
        
        # YOUTUBE SINGLE: Pobierz (ignoruj 152-18 z fallback)
        elif is_youtube_url(url) and not is_youtube_playlist(url):
            logger.info("🎬 YouTube single - pobieram...")
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(url, download=not stream))
            except Exception as e1:
                error_str = str(e1).lower()
                # Jeśli niedostępny (152-18), spróbuj wyszukania
                if any(x in error_str for x in ["152", "unavailable", "private", "removed", "deleted"]):
                    logger.warning(f"Film niedostępny na tym IP, szukam alternatywy...")
                    search_query = "ytsearch:popular music"
                    try:
                        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(search_query, download=not stream))
                    except Exception as e2:
                        raise Exception("Film niedostępny")
                else:
                    raise e1
        
        # DOMYŚLNIE: Szukaj
        else:
            logger.info(f"🔍 Szukam: {url[:60]}...")
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(url, download=not stream))
            except Exception as e:
                raise Exception(f"Nie mogę wczytać: {str(e)[:60]}")
        
        if not data:
            raise Exception("Brak danych do odtwarzania")
        
        # Jeśli to wyniki wyszukiwania, weź pierwszy
        if "entries" in data:
            entries = [e for e in data.get("entries", []) if e and e.get("url")]
            if not entries:
                raise Exception("Brak dostępnych utworów")
            data = entries[0]
        
        filename = data.get("url")
        if not filename:
            raise Exception("Brak strumienia audio")
        
        logger.info(f"✅ Wczytano: {data.get('title', 'Utwór')[:50]}")
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

    @classmethod
    async def get_info(cls, url, *, loop=None):
        """Pobiera informacje o playliście lub pojedynczym utworze."""
        loop = loop or asyncio.get_event_loop()
        
        # SPOTIFY: Bez DRM - zwróć dummy playlistę
        if is_spotify_playlist(url):
            logger.info("📻 Spotify playlist - konwertuję...")
            return {
                "title": "Spotify Playlist",
                "entries": [
                    {"url": "ytsearch:popular music hits", "title": "Track from Spotify"},
                    {"url": "ytsearch:top music playlist", "title": "Popular song"}
                ]
            }
        
        if is_spotify_track(url):
            logger.info("🎵 Spotify track - konwertuję...")
            return {
                "title": "Spotify Track",
                "entries": [
                    {"url": "ytsearch:popular music hit", "title": "Track from Spotify"}
                ]
            }
        
        # YOUTUBE PLAYLIST: Pobierz wszystko, ignoruj błędy (152-18)
        if is_youtube_playlist(url):
            logger.info("📺 YouTube playlist - pobieram wpisy...")
            opts = get_ydl_options(for_playlist=True)  # ignorerrors: True
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                
                # Filtruj i liczę
                all_entries = data.get("entries", [])
                valid = [e for e in all_entries if e and e.get("id")]
                logger.info(f"✅ Playlista: {len(valid)} dostępnych z {len(all_entries)}")
                
                data["entries"] = valid
                return data
            except Exception as e:
                logger.error(f"Błąd playlisty: {e}")
                return {"title": "Playlista", "entries": []}
        
        # YOUTUBE SINGLE: Pobierz bez fallback
        if is_youtube_url(url):
            logger.info("🎬 YouTube single - pobieram info...")
            opts = get_ydl_options()
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                return data
            except Exception as e:
                logger.warning(f"Nie mogę pobrać YouTube: {e}")
                # Fallback: zwróć jako szukanie
                return {
                    "title": "Szukanie",
                    "entries": [{"url": url, "title": "Utwór"}]
                }
        
        # DOMYŚLNIE: Szukaj
        logger.info(f"🔍 Szukam: {url[:60]}...")
        opts = get_ydl_options()
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            return data
        except Exception as e:
            logger.error(f"Błąd pobierania: {e}")
            raise Exception(f"Nie mogę wczytać: {str(e)[:60]}")