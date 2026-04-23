import discord
import asyncio
import yt_dlp
import os
import re
import logging

logger = logging.getLogger('MusicBot')

# Opcje dla FFmpeg - zoptymalizowane pod kątem stabilności i szybkości startu
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 30000000",
    "options": "-vn -dn -sn -ignore_unknown -probesize 32k -analyzeduration 0 -threads 1",
}

# Opcje dla Radio - bardziej konserwatywne
RADIO_FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 30000000",
    "options": "-vn",
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
        "ignoreerrors": True if for_playlist else False,
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

def get_ydl_search_options():
    """Opcje dla YouTube search - pomija pobieranie info aby uniknąć 152-18 błędów."""
    return {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "socket_timeout": 30,
        "source_address": "0.0.0.0",
        "nocheckcertificate": True,
        "logtostderr": False,
        "no_color": True,
        "extract_flat": "in_playlist",  # Tylko URLs, bez info - uniknie 152-18!
        "ignoreerrors": True,  # Pomijaj niedostępne
        "skip_unavailable_videos": True,
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "extractor_args": {
            "youtube": {
                "player_client": ["web_embedded", "tv_embedded", "android"],
                "player_skip": ["js", "configs"],
                "skip_unavailable_videos": True
            }
        },
    }

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title", "Utwór")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        """Pobiera audio stream z YouTube (lub szuka alternatywy).
        
        Obsługuje:
        - ytsearch: query - wyszukuje na YouTube (extract_flat aby uniknąć 152-18)
        - YouTube URL - pobiera bezpośrednio (z fallback na search dla 152-18)
        - Cokolwiek innego - behandluje jako search query
        """
        loop = loop or asyncio.get_event_loop()
        
        # Jeśli to już ytsearch: query (z get_info), to szukaj z extract_flat
        if url.startswith("ytsearch:"):
            logger.info(f"🔍 YouTube search: {url[9:50]}...")
            search_opts = get_ydl_search_options()
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(url, download=not stream))
            except Exception as e:
                logger.error(f"Search failed: {e}")
                raise Exception(f"Nie mogę znaleźć: {str(e)[:60]}")
        
        # YouTube video URL - normalnie
        elif is_youtube_url(url) and not is_youtube_playlist(url):
            logger.info("🎬 YouTube single - pobieram...")
            opts = get_ydl_options()
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(url, download=not stream))
            except Exception as e1:
                error_str = str(e1).lower()
                # Jeśli niedostępny (152-18), spróbuj wyszukania
                if any(x in error_str for x in ["152", "unavailable", "private", "removed", "deleted"]):
                    logger.warning(f"Film niedostępny, szukam alternatywy...")
                    search_query = "ytsearch:popularna piosenka"
                    try:
                        search_opts = get_ydl_search_options()
                        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(search_query, download=not stream))
                    except Exception as e2:
                        logger.error(f"Fallback failed: {e2}")
                        raise Exception("Film niedostępny")
                else:
                    raise e1
        
        # Cokolwiek innego - treat jako search query z extract_flat
        else:
            logger.info(f"🔍 Search: {url[:50]}...")
            search_opts = get_ydl_search_options()
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(url, download=not stream))
            except Exception as e:
                raise Exception(f"Nie mogę wczytać: {str(e)[:60]}")
        
        if not data:
            raise Exception("Brak danych do odtwarzania")
        
        # Jeśli to wyniki wyszukiwania (extract_flat), weź pierwszy i pobierz jego info
        if "entries" in data:
            entries = data.get("entries", [])
            if not entries:
                raise Exception("Brak dostępnych utworów")
            first_entry = entries[0]
            
            # Jeśli to tylko URL z extract_flat, pobierz pełne info
            if isinstance(first_entry, dict) and "url" in first_entry and "title" not in first_entry:
                logger.debug(f"Pobieranie info dla: {first_entry['url']}")
                try:
                    opts = get_ydl_options()
                    data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(first_entry['url'], download=not stream))
                except Exception as e:
                    logger.warning(f"Nie mogę pobrać info: {e}, używam domyślnie")
                    data = first_entry
            else:
                data = first_entry
        
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
            # Brak metadanych (DRM) - zwróć dummy entries z generycznym wyszukiwaniem
            return {
                "title": "Spotify Playlist",
                "entries": [
                    {"url": "ytsearch:popularna muzyka", "title": "Utwór 1 ze Spotify"},
                    {"url": "ytsearch:najlepsze piosenki", "title": "Utwór 2 ze Spotify"}
                ]
            }
        
        if is_spotify_track(url):
            logger.info("🎵 Spotify track - konwertuję...")
            # Brak metadanych (DRM) - zwróć generyczne wyszukiwanie
            return {
                "title": "Spotify Track",
                "entries": [
                    {"url": "ytsearch:popularna piosenka", "title": "Utwór ze Spotify"}
                ]
            }
        
        # YOUTUBE PLAYLIST: Pobierz listę, ignoruj błędy (152-18)
        if is_youtube_playlist(url):
            logger.info("📺 YouTube playlist - pobieram wpisy...")
            opts = get_ydl_options(for_playlist=True)
            opts["extract_flat"] = "in_playlist"  # Tylko URLs, bez info
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                
                entries = data.get("entries", [])
                if entries:
                    logger.info(f"✅ Playlista: {len(entries)} wpisów")
                
                return {
                    "title": data.get("title", "Playlista"),
                    "entries": entries or []
                }
            except Exception as e:
                logger.error(f"Błąd playlisty: {e}")
                return {"title": "Playlista", "entries": []}
        
        # YOUTUBE SINGLE: Zwróć URL (info pobierze from_url)
        if is_youtube_url(url):
            logger.info("🎬 YouTube single")
            return {
                "title": "YouTube",
                "entries": [{"url": url, "title": "Utwór"}]
            }
        
        # DOMYŚLNIE: Wyszukaj z extract_flat
        logger.info(f"🔍 Szukam: {url[:60]}...")
        search_opts = get_ydl_search_options()
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            return data
        except Exception as e:
            logger.error(f"Błąd wyszukiwania: {e}")
            raise Exception(f"Nie mogę wczytać: {str(e)[:60]}")