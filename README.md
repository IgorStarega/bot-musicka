# 🎵 Bot Musicka

Podstawowy bot muzyczny na Discorda obsługujący YouTube, Spotify oraz Twoje ulubione stacje radiowe.

**Wersja:** 1.5.0 (Optymalizacja & Cleanup)
**Język:** Python 3.11+
**Technologia:** discord.py, yt-dlp, FFmpeg
**Status:** Production-Ready ✅

## 🚀 Funkcje
- 📻 **Stacje Radiowe:** Dynamiczne pobieranie stacji z API (w tym obsługa OpenFM).
- 📺 **YouTube:** Odtwarzanie muzyki, playlist i omijanie blokad (cookies/mobilne API).
- 🎵 **Spotify:** Pełne wsparcie dla playlist - konwersja na wysoką jakość z YouTube (Tytuł + Wykonawca).
- 📋 **System Kolejki:** Widoczna lista utworów pod komendą `/queue`.
- ⭐ **Ulubione & Historia:** Zapisuj ulubione utwory i przeglądaj ostatnie słuchane (v1.3.0).
- 📊 **Statystyki:** Szczegółowe statystyki użytkownika (`/mystats`) (v1.3.0).
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
- `user_storage.py` - System przechowywania ulubionych, historii i statystyk (v1.3.0).
- `IDEAS.md` - Dokumentacja techniczna zmian, analiza ryzyk i roadmapa 2.0.

## 📋 Lista Komend

### Odtwarzanie Muzyki
- `/play [link/fraza]` - Odtwarzanie muzyki lub playlist (YT/Spotify). Automatyczne fallback na wyszukiwanie jeśli niedostępne.
- `/radio [ID]` - Odtwarzanie stacji radiowej z API (z autocomplete).
- `/list_radio` - Lista dostępnych stacji radiowych.
- `/queue` - Podgląd kolejki z tytułami (pierwsze 10 utworów).
- `/skip` - Pominięcie aktualnego utworu.
- `/stop` - Zatrzymanie i czyszczenie kolejki.
- `/pause` - Wstrzymanie odtwarzania.
- `/resume` - Wznowienie odtwarzania po pauzie.
- `/volume [0-100]` - Zmiana głośności bota.
- `/disconnect` - Odłącz bota z kanału i wyczyść kolejkę.

### Statystyki & Zarządzanie
- `/nowplaying` - Info o aktualnie grającym utworze.
- `/history` - Historia ostatnio granych utworów (ostatnie 20).
- `/favorites` - Lista ulubionych utworów.
- `/favorite [add|remove]` - Dodaj/usuń do ulubionych (wybór z listy).
- `/mystats` - Twoje statystyki (grane utwory, skipy, ulubione).

### Diagnostyka
- `/status` - Diagnostyka bota (Discord, FFmpeg, Radio API, Ping).
- `/test` - Test wszystkich komponentów bota.

## 🔄 Ostatnie Poprawki (v1.5.0)
- ✅ Nowa komenda `/disconnect` - odłącz bota i wyczyść kolejkę.
- ✅ `/queue` wyświetla teraz tytuły zamiast surowych URL-i.
- ✅ `/favorite` - proper slash-command choices (add/remove) zamiast wolnego tekstu.
- ✅ Naprawiony bug: `play_next()` nie crashował gdy `from_url()` zwracało `None`.
- ✅ Kolejka przechowuje tytuły dla poprawnego wyświetlania.
- ✅ Zredukowane nadmiarowe logi INFO → DEBUG w `music_handler.py`.
- ✅ `config.py` używa teraz `logger` zamiast `print()`.
- ✅ Usunięte stare tagi `(v1.3.0)` z opisów komend.

---
Autor: Bot Musicka Team
Data: 27 kwietnia 2026
Wersja: 1.5.0 (Optymalizacja & Cleanup)
