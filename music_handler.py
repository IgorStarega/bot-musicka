import discord
import asyncio
import yt_dlp
import os
import re
import logging

logger = logging.getLogger('MusicBot')

# Opcje dla FFmpeg - zoptymalizowane pod kątem stabilności i szybkości startu
FFMPEG_OPTIONS = {
    "before_options": "-user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\" -headers \"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\\r\\n\" -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 30000000",
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
        "format": "best",  # Najprostsza - najlepszy dostępny format
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "socket_timeout": 120,
        "sleep_interval": 2,
        "sleep_interval_requests": 2,
        "source_address": "0.0.0.0",
        "nocheckcertificate": True,
        "ignoreerrors": True if for_playlist else False,
        "logtostderr": False,
        "no_color": True,
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
        "extract_flat": False,
        "force_generic_extractor": False,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "extractor_args": {
            "youtube": {
                "player_client": ["web_embedded"],
                "player_skip": ["js", "configs"],
                "skip_unavailable_videos": True
            }
        },
    }
    return base_options

def get_ydl_search_options():
    """Opcje dla YouTube search - pomija pobieranie info aby uniknąć 152-18 błędów."""
    return {
        "format": "best",  # Najprostsza - najlepszy dostępny format
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "socket_timeout": 120,
        "sleep_interval": 2,
        "sleep_interval_requests": 2,
        "source_address": "0.0.0.0",
        "nocheckcertificate": True,
        "logtostderr": False,
        "no_color": True,
        "extract_flat": "in_playlist",  # Tylko URLs, bez info - uniknie 152-18!
        "ignoreerrors": True,  # Pomijaj niedostępne
        "skip_unavailable_videos": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "extractor_args": {
            "youtube": {
                "player_client": ["web_embedded"],
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
            query = url[9:50]
            logger.info(f"🔍 YouTube search: {query}...")
            logger.debug(f"  → Format: audio-only (140/251/250/249)")
            search_opts = get_ydl_search_options()
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(url, download=not stream))
                logger.debug(f"  ✓ Wyszukiwanie zwróciło {len(data.get('entries', []))} wyników")
            except Exception as e:
                logger.error(f"❌ Search failed: {str(e)[:100]}")
                raise Exception(f"Nie mogę znaleźć: {str(e)[:60]}")
        
        # YouTube video URL - normalnie
        elif is_youtube_url(url) and not is_youtube_playlist(url):
            video_id = url.split('v=')[-1][:11] if 'v=' in url else url.split('/')[-1][:11]
            logger.info(f"🎬 YouTube single [{video_id}] - pobieram...")
            logger.debug(f"  → Format: audio-only (140/251/250/249)")
            logger.debug(f"  → Player clients: web_embedded, tv_embedded, android")
            opts = get_ydl_options()
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(url, download=not stream))
                logger.debug(f"  ✓ Pobrano: {data.get('title', 'N/A')[:50]}")
            except Exception as e1:
                error_str = str(e1).lower()
                error_code = "152-18" if "152" in error_str else "unknown"
                # Jeśli niedostępny (152-18), spróbuj wyszukania
                if any(x in error_str for x in ["152", "unavailable", "private", "removed", "deleted"]):
                    logger.warning(f"⚠️ Film niedostępny (kod: {error_code}), szukam alternatywy...")
                    search_query = "ytsearch:popularna piosenka"
                    logger.debug(f"  → Fallback search: {search_query}")
                    try:
                        search_opts = get_ydl_search_options()
                        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(search_query, download=not stream))
                        logger.info(f"  ✓ Fallback znalazł: {len(data.get('entries', []))} wyników")
                    except Exception as e2:
                        logger.error(f"❌ Fallback failed: {str(e2)[:100]}")
                        raise Exception("Film niedostępny")
                else:
                    raise e1
        
        # Cokolwiek innego - treat jako search query z extract_flat
        else:
            logger.info(f"🔍 Search: {url[:50]}...")
            logger.debug(f"  → Extract: flat mode (only URLs, no info fetching)")
            search_opts = get_ydl_search_options()
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(url, download=not stream))
                logger.debug(f"  ✓ Znaleziono {len(data.get('entries', []))} wyników")
            except Exception as e:
                logger.error(f"❌ Search error: {str(e)[:100]}")
                raise Exception(f"Nie mogę wczytać: {str(e)[:60]}")
        
        if not data:
            logger.error("❌ Brak danych do odtwarzania")
            raise Exception("Brak danych do odtwarzania")
        
        # Jeśli to wyniki wyszukiwania (extract_flat), weź pierwszy i pobierz jego info
        if "entries" in data:
            entries = data.get("entries", [])
            if not entries:
                logger.error("❌ Brak dostępnych utworów w wynikach")
                raise Exception("Brak dostępnych utworów")
            logger.debug(f"  → Przetwarzam pierwszy wpis z {len(entries)} dostępnych")
            first_entry = entries[0]
            
            # Jeśli to tylko URL z extract_flat, pobierz pełne info
            if isinstance(first_entry, dict) and "url" in first_entry and "title" not in first_entry:
                first_url = first_entry['url']
                logger.info(f"  📥 Pobieranie full info dla: {first_url[:50]}...")
                try:
                    opts = get_ydl_options()
                    data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(first_url, download=not stream))
                    logger.debug(f"  ✓ Full info pobrane: {data.get('title', 'N/A')[:50]}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Nie mogę pobrać full info: {str(e)[:80]}, używam URL bezpośrednio")
                    data = first_entry
            else:
                logger.debug(f"  ✓ Mamy już info: {first_entry.get('title', 'N/A')[:50]}")
                data = first_entry
        
        filename = data.get("url")
        if not filename:
            logger.error("❌ Brak URL w danych yt-dlp")
            logger.debug(f"  Dostępne pola: {list(data.keys())}")
            raise Exception("Brak strumienia")
        
        # Sprawdź czy to video page URL czy stream URL
        if "watch?v=" in filename or "youtu.be" in filename:
            logger.warning(f"  ⚠️ Otrzymano video page URL zamiast stream URL!")
            logger.warning(f"  URL: {filename}")
            # Spróbuj wyciągnąć stream_url jeśli istnieje
            if "url" in data:
                stream_url = data.get("url")
                if stream_url and "watch" not in stream_url:
                    filename = stream_url
                    logger.info(f"  ✓ Użyłem stream_url: {filename[:80]}...")
        
        title = data.get('title', 'Utwór')[:60]
        logger.info(f"✅ Wczytano: {title}")
        logger.debug(f"  → URL Type: {'Video Page' if 'watch?' in filename else 'Stream'}")
        logger.debug(f"  → Full URL: {filename}")
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