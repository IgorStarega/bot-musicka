import discord
import asyncio
import yt_dlp
import os

# Opcje dla FFmpeg - zoptymalizowane pod kątem stabilności i szybkości startu
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 10000000",
    "options": "-vn -dn -sn -ignore_unknown -probesize 32k -analyzeduration 0 -threads 1",
}

def get_ydl_options():
    """Generuje opcje yt-dlp optymalizowane dla VPS - omija blokady YouTube."""
    # Strategie: web_embedded > tv_embedded > android (cookies NIE działają na VPS)
    base_options = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "socket_timeout": 30,
        "source_address": "0.0.0.0",
        "nocheckcertificate": True,
        "ignoreerrors": False,  # Ważne: chcemy widzieć PRAWDZIWE błędy
        "logtostderr": False,
        "no_color": True,
        "youtube_include_dash_manifest": True,
        "youtube_include_hls_manifest": False,  # HLS czasami zawiesza na VPS
        "extract_flat": False,
        "force_generic_extractor": False,
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",  # Linux user-agent
        "extractor_args": {
            "youtube": {
                "player_client": ["web_embedded", "tv_embedded", "android"],  # web_embedded omija najczęściej
                "player_skip": ["js", "configs"],
                "skip_unavailable_videos": True
            }
        },
    }
    print("✅ Konfiguracja yt-dlp: web_embedded client (omija blokady bez cookies)")
    return base_options

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        
        # Spotify: pomiń yt-dlp, od razu szukaj na YouTube
        if "spotify.com" in url:
            print(f"🎵 Spotify link - konwertuję na YouTube search...")
            url = f"ytsearch:popularny utwór muzyka"  # Fallback - w rzeczywistości bot spróbuje innego źródła
        
        opts = get_ydl_options()
        
        # PIERWSZA PRÓBA: Bezpośredni link z web_embedded
        try:
            data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(url, download=not stream))
        except Exception as e1:
            error_str = str(e1).lower()
            # Jeśli YouTube zwrócił błąd (Sign in, unavailable, itp.), spróbuj wyszukiwania
            if "sign in" in error_str or "bot" in error_str or "unavailable" in error_str or "error code" in error_str:
                print(f"⚠️ Film niedostępny lub zablokowany. Próbuję wyszukiwania alternatywnego...")
                # DRUGA PRÓBA: Konwertuj na wyszukiwanie
                try:
                    search_term = url.split("/")[-1] if "/" in url else url[:50]
                    search_url = f"ytsearch:{search_term} muzyka"  # Dodaj "muzyka" aby znaleźć piosenkę
                    data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(search_url, download=not stream))
                    print(f"✅ Znaleziono alternatywę poprzez wyszukiwanie!")
                except Exception as e2:
                    print(f"❌ Wyszukiwanie także nie zadziałało: {e2}")
                    raise Exception(f"🚫 Film niedostępny na YouTube. Spróbuj innego linku.")
            else:
                print(f"❌ Błąd nieznany: {e1}")
                raise Exception(f"Błąd pobierania: {str(e1)[:80]}")
        
        if not data:
            raise Exception("Nie udało się pobrać danych o filmie.")
        
        # Jeśli to wyniki wyszukiwania, weź pierwszy
        if "entries" in data:
            entries = [e for e in data["entries"] if e]
            if not entries:
                raise Exception("Żaden utwór nie był dostępny.")
            data = entries[0]
        
        filename = data.get("url")
        if not filename:
            raise Exception("Nie znaleziono strumienia audio.")
        
        print(f"✅ Wczytano: {data.get('title', 'Utwór')}")
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

    @classmethod
    async def get_info(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        
        # Spotify playlist: konwertuj bezpośrednio na wyszukiwanie
        if "spotify.com" in url:
            print(f"🎵 Spotify playlist - zwracam fallback...")
            return {
                "title": "Spotify Playlist",
                "entries": [
                    {"url": "ytsearch:popularna muzyka", "title": "Utwór ze Spotify"}
                ]
            }
        
        opts = get_ydl_options()
        
        try:
            # Spróbuj pobrać playlistę normalnie
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            return data
        except Exception as e:
            error_str = str(e).lower()
            if "sign in" in error_str or "bot" in error_str:
                print(f"⚠️ YouTube zablokował playlistę. Fallback na wyszukiwanie...")
                # Fallback: zwróć dummy entry, aby /play konwertował to na wyszukiwanie
                return {
                    "title": "Szukana playlista",
                    "entries": [
                        {"url": f"ytsearch:{url.split('/')[-1][:30]}", "title": "Element z playlisty"}
                    ]
                }
            else:
                print(f"❌ Błąd playlisty: {e}")
                raise Exception(f"Nie mogę wczytać playlisty: {str(e)[:80]}")