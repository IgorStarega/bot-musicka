import discord
import asyncio
import yt_dlp
import os
import re
from urllib.parse import urlparse, parse_qs

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
    # playlist?list=... lub /playlist?...
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
        opts = get_ydl_options()
        
        # SPOTIFY SINGLE: Wyciągnij metadane i szukaj na YouTube
        if is_spotify_track(url):
            print(f"🎵 Spotify track - konwertuję na YouTube search...")
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                    artist = info.get("artist", "Nieznany artysta")
                    title = info.get("title", "Nieznany utwór")
                    search_url = f"ytsearch:{artist} - {title}"
                    print(f"🔍 Szukam na YouTube: {artist} - {title}")
                    data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(search_url, download=not stream))
            except Exception as e:
                print(f"⚠️ Spotify fallback nie zadziałał, szukam domyślnie...")
                search_url = f"ytsearch:popularna muzyka"
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(search_url, download=not stream))
        
        # YOUTUBE: Bezpośredni link
        elif is_youtube_url(url) and not is_youtube_playlist(url):
            print(f"🎬 YouTube single - próbuję pobrać...")
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(url, download=not stream))
            except Exception as e1:
                error_str = str(e1).lower()
                if "sign in" in error_str or "bot" in error_str or "unavailable" in error_str or "error code" in error_str:
                    print(f"⚠️ Film niedostępny (kod 152-18). Pomijacie...")
                    raise Exception(f"🚫 Film niedostępny - spróbuj innego linku.")
                else:
                    raise e1
        
        # POZOSTAŁE: Domyślna obsługa
        else:
            try:
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(opts).extract_info(url, download=not stream))
            except Exception as e:
                raise e
        
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
        opts = get_ydl_options()
        
        # SPOTIFY SINGLE: Konwertuj na YouTube search
        if is_spotify_track(url):
            print(f"🎵 Spotify track - zwracam jako wyszukiwanie...")
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                    artist = info.get("artist", "Nieznany artysta")
                    title = info.get("title", "Nieznany utwór")
                    return {
                        "title": f"{artist} - {title}",
                        "entries": [
                            {"url": f"ytsearch:{artist} - {title}", "title": f"{artist} - {title}"}
                        ]
                    }
            except Exception as e:
                print(f"⚠️ Nie mogę pobrać metadanych Spotify: {e}")
                return {
                    "title": "Utwór Spotify",
                    "entries": [{"url": "ytsearch:popularna muzyka", "title": "Utwór"}]
                }
        
        # SPOTIFY PLAYLIST: Iteruj po utwórach i konwertuj każdy
        elif is_spotify_playlist(url):
            print(f"📻 Spotify playlist - konwertuję utwory...")
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                    entries = []
                    for entry in info.get("entries", []):
                        if entry:
                            artist = entry.get("artist", "Nieznany artysta")
                            title = entry.get("title", "Nieznany utwór")
                            entries.append({
                                "url": f"ytsearch:{artist} - {title}",
                                "title": f"{artist} - {title}"
                            })
                    if entries:
                        return {
                            "title": info.get("title", "Spotify Playlist"),
                            "entries": entries
                        }
            except Exception as e:
                print(f"⚠️ Błąd Spotify playlist: {e}")
            
            # Fallback dla Spotify playlisty
            return {
                "title": "Spotify Playlist",
                "entries": [{"url": "ytsearch:popularna muzyka", "title": "Utwór ze Spotify"}]
            }
        
        # YOUTUBE PLAYLIST: Pobierz wszystkie dostępne wpisy
        elif is_youtube_playlist(url):
            print(f"📺 YouTube playlist - pobieram wszystkie wpisy...")
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                
                # Filtruj niedostępne wpisy
                valid_entries = []
                for entry in data.get("entries", []):
                    if entry and entry.get("id"):  # Sprawdzenie czy entry ma ID (jest dostępny)
                        valid_entries.append(entry)
                
                print(f"✅ Playlista: {len(valid_entries)} dostępnych / {len(data.get('entries', []))} ogółem")
                data["entries"] = valid_entries
                return data
            except Exception as e:
                error_str = str(e).lower()
                print(f"⚠️ Błąd playlisty YouTube: {e}")
                return {"title": "Playlista", "entries": []}  # Pusta lista
        
        # DOMYŚLNIE: Normalne pobieranie
        else:
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                return data
            except Exception as e:
                print(f"❌ Błąd pobierania: {e}")
                raise Exception(f"Nie mogę wczytać: {str(e)[:80]}")