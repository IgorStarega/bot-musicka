# 🎵 Bot Musicka

Podstawowy bot muzyczny na Discorda obsługujący YouTube, Spotify oraz Twoje ulubione stacje radiowe.

**Wersja:** 1.0.0 (Stabilna)
**Język:** Python 3.11+
**Technologia:** discord.py, yt-dlp, FFmpeg

## 🚀 Funkcje
- 📻 **Stacje Radiowe:** Obsługa 11 predefiniowanych stacji (Radioparty, RMF MAXX, ESKA, Radio ZET, Open FM).
- 📺 **YouTube:** Odtwarzanie muzyki z linków i wyszukiwanie fraz.
- 🎵 **Spotify:** Podstawowe wsparcie dla linków Spotify (wyszukiwanie przez yt-dlp).
- 🐚 **Slash Commands:** Intuicyjne sterowanie za pomocą `/`.
- 🐳 **Docker:** Gotowe pliki konfiguracyjne do szybkiego wdrożenia.

## 🛠️ Instalacja Lokalna

1. **Sklonuj repozytorium:**
   ```bash
   git clone <link-do-twojego-repo>
   cd bot-musicka
   ```

2. **Skonfiguruj środowisko:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Po polsku: .venv\Scripts\activate dla Windows
   pip install -r requirements.txt
   ```

3. **Uzupełnij Token:**
   - Skopiuj plik `.env` (jeśli nie istnieje, stwórz go).
   - Wpisz swój token: `DISCORD_TOKEN=Twój_Token_Tutaj`.

4. **FFmpeg:**
   - Upewnij się, że masz zainstalowany FFmpeg w systemie.

5. **Uruchom:**
   ```bash
   python main.py
   ```

## 🐳 Wdrożenie Docker (Zalecane)

1. **Uruchomienie za pomocą Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   *Pamiętaj o wypełnieniu pliku `.env` przed uruchomieniem.*

## 📁 Struktura Projektu
- `main.py` - Główne serce bota i komendy slash.
- `music_handler.py` - Logika odtwarzania i yt-dlp.
- `config.py` - Konfiguracja i lista stacji.
- `Dockerfile` & `docker-compose.yml` - Konteneryzacja.
- `.env` - Dane wrażliwe (token).

## 📋 Lista Komend
- `/join` - Dołączenie do kanału głosowego.
- `/play [query]` - Odtwarzanie muzyki.
- `/radio [ID]` - Wybór stacji (1-11).
- `/stop` - Zatrzymanie muzyki.
- `/leave` - Opuszczenie kanału.
- `/ping` - Test opóźnienia.
- `/test` - Diagnostyka bota.

## 🔄 Najnowsze Aktualizacje (v1.0.0)
- Dodano obsługę plików `.env`.
- Wdrożono konteneryzację Docker.
- Skonfigurowano CI/CD przez GitHub Actions (GHCR).
- Dodano automatyczne ponowne połączenie strumienia (FFmpeg reconnect).

---
Autor: Bot Musicka Team
Data: 23 kwietnia 2026
