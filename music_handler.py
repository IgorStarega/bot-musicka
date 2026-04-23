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
    """Generuje opcje yt-dlp z dynamicznym sprawdzaniem cookies i omijaniem blokad."""
    base_options = {
        "format": "bestaudio/best",
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "source_address": "0.0.0.0",
        "nocheckcertificate": True,
        "ignoreerrors": True,
        "logtostderr": False,
        "no_color": True,
        "youtube_include_dash_manifest": True,
        "youtube_include_hls_manifest": True,
        "extract_flat": False,
        "force_generic_extractor": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "extractor_args": {
            "youtubetab": ["skip=authcheck"],
            "youtube": {
                "player_client": ["android", "ios", "web"],
                "player_skip": ["webpage", "configs"]
            }
        },
    }
    
    # Próba znalezienia ciasteczek
    cookie_paths = ["/app/config/cookies.txt", "config/cookies.txt", "cookies.txt"]
    for path in cookie_paths:
        if os.path.exists(path):
            try:
                if os.path.getsize(path) > 100:
                    print(f"✅ Znaleziono plik cookies: {path}")
                    base_options["cookiefile"] = path
                    break
            except Exception:
                continue
    else:
        print("⚠️ OSTRZEŻENIE: Brak pliku cookies.txt! YouTube może blokować odtwarzanie.")
        
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
        
        # Specjalna obsługa Spotify - konwersja linku na wyszukiwanie w YouTube
        if "spotify.com" in url:
            with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
                try:
                    # Pobieramy tylko metadane ze Spotify (tytuł i wykonawca)
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False, process=True))
                    if info:
                        # Sprawdzamy czy to playlista czy pojedynczy utwor
                        track_title = info.get('title')
                        track_artist = info.get('artist', '') or info.get('uploader', '')
                        search_term = f"{track_title} {track_artist}".strip()
                        url = f"ytsearch:{search_term}"
                        print(f"Konwersja Spotify -> YouTube: {search_term}")
                except Exception as e:
                    print(f"Błąd ekstrakcji Spotify: {e}, próbuję linku bezpośrednio...")
            
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            # Próba pobrania bezpośredniego info (lub wyszukiwania po konwersji)
            try:
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=not stream))
            except Exception as e:
                # Jeśli błąd formatu, spróbuj wyszukać tytuł zamiast bezpośredniego linku
                print(f"Błąd bezpośredni: {e}, próbuję wyszukiwania...")
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{url}", download=not stream))
            
            if not data:
                raise Exception("Nie udało się pobrać informacji o filmie.")

            if "entries" in data:
                # Wybierz pierwszy działający wynik z listy
                entries = [e for e in data["entries"] if e]
                if not entries:
                    raise Exception("Brak dostępnych formatów dla tego utworu.")
                data = entries[0]

            filename = data.get("url")
            if not filename:
                raise Exception("Nie znaleziono strumienia audio.")

            return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

    @classmethod
    async def get_info(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        
        # Obsługa playlist Spotify
        if "spotify.com" in url:
            opts = get_ydl_options()
            opts["extract_flat"] = "in_playlist"
            with yt_dlp.YoutubeDL(opts) as ydl:
                try:
                    data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                    if data and "entries" in data and data["entries"] is not None:
                        # Przetwarzamy każdy element na zapytanie wyszukiwania YouTube
                        new_entries = []
                        for entry in data["entries"]:
                            if entry:
                                artist = entry.get("artist") or entry.get("uploader") or ""
                                title = entry.get("title") or "Nieznany utwór"
                                # Dodajemy informację o oryginalnym tytule do wyszukiwania
                                entry["url"] = f"ytsearch:{title} {artist}".strip()
                                new_entries.append(entry)
                        data["entries"] = new_entries
                    return data
                except Exception as e:
                    print(f"Błąd pobierania info Spotify: {e}")
        
        opts = get_ydl_options()
        # Dla playlist YouTube chcemy tylko metadane bez rozwijania ich tutaj, 
        # chyba że to faktycznie wezwanie do pobrania info o liście.
        with yt_dlp.YoutubeDL(opts) as ydl:
            return await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))