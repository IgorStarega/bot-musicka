# 🎵 Bot Musicka

Podstawowy bot muzyczny na Discorda obsługujący YouTube, Spotify oraz Twoje ulubione stacje radiowe.

**Wersja:** 1.1.0 (Stabilna + Optymalizowana)
**Język:** Python 3.11+
**Technologia:** discord.py, yt-dlp, FFmpeg

## 🚀 Funkcje
- 📻 **Stacje Radiowe:** Dynamiczne pobieranie stacji z API (w tym obsługa OpenFM).
- 📺 **YouTube:** Odtwarzanie muzyki, playlist i omijanie blokad (cookies/mobilne API).
- 🎵 **Spotify:** Pełne wsparcie dla playlist - konwersja na wysoką jakość z YouTube (Tytuł + Wykonawca).
- 📋 **System Kolejki:** Widoczna lista utworów pod komendą `/queue`.
- 🐚 **Slash Commands:** Intuicyjne sterowanie za pomocą `/`.
- 🐳 **Docker:** Gotowe pliki konfiguracyjne do szybkiego wdrożenia na VPS.
- 📉 **Auto-Leave:** Automatyczne oszczędzanie zasobów po opuszczeniu kanału przez ludzi.

## 🛠️ Instalacja i Uruchomienie (Docker)

1. **Skonfiguruj plik `.env`**:
   `DISCORD_TOKEN=Twój_Token_Tutaj`

2. **Dodaj ciasteczka (Zalecane)**:
   Umieść `cookies.txt` w folderze `config/`, aby uniknąć błędów "Sign in to confirm you're not a bot".

3. **Uruchomienie bota**:
   ```bash
   docker compose up -d --build
   ```

## 📁 Struktura Projektu
- `main.py` - Główne serce bota, komendy slash i system logowania (`bot.log`).
- `music_handler.py` - Zaawansowana logika odtwarzania, optymalizacja FFmpeg i konwersja Spotify.
- `config.py` - Dynamiczne Radio API i konfiguracja środowiska.
- `IDEAS.md` - Dokumentacja techniczna zmian, analiza ryzyk i roadmapa 2.0.

## 📋 Lista Komend
- `/play [link/fraza]` - Odtwarzanie muzyki lub playlist (YT/Spotify). Automatyczne fallback na wyszukiwanie jeśli niedostępne.
- `/radio [ID]` - Odtwarzanie stacji radiowej z API (z autocomplete).
- `/list_radio` - Lista dostępnych stacji radiowych.
- `/queue` - Podgląd kolejki (pierwsze 10 utworów).
- `/skip` - Pominięcie aktualnego utworu.
- `/stop` - Zatrzymanie i czyszczenie kolejki.
- `/status` - Diagnostyka bota (Discord, FFmpeg, Radio API, Ping).
- `/test` - Test wszystkich komponentów bota.

## 🔄 Ostatnie Poprawki (v1.1.0)
- ✅ Naprawiono błąd `NoneType` przy wczytywaniu playlist.
- ✅ Dodano profesjonalny system logowania do pliku `bot.log`.
- ✅ Poprawiono wyszukiwanie piosenek ze Spotify (bez DRM).
- ✅ Zoptymalizowano parametry FFmpeg dla szybszego startu audio.
- ✅ Fallback na wyszukiwanie dla niedostępnych filmów YouTube (152-18).
- ✅ Auto-Leave: Bot wychodzi gdy zostanie sam na kanale.
- ✅ Dodano komendy `/status` i `/test` do diagnostyki.
- ✅ System autocomplete dla `/radio` z filtrowaniem stacji.
- ✅ Dodano komendę `/queue` do podglądu kolejki.

---
Autor: Bot Musicka Team
Data: 23 kwietnia 2026
