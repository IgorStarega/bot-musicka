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

## 🛠️ Instalacja na Linux (Ubuntu/Debian)

1. **Zaktualizuj system i zainstaluj zależności:**
   ```bash
   sudo apt update && sudo apt install -y github-cli ffmpeg python3-pip python3-venv
   ```

2. **Sklonuj repozytorium:**
   ```bash
   git clone <link-do-twojego-repo>
   cd bot-musicka
   ```

3. **Skonfiguruj środowisko:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Uzupełnij Token:**
   - Edytuj `.env` (np. `nano .env`):
     `DISCORD_TOKEN=Twój_Token_Tutaj`

5. **Uruchomienie w tle (Systemd - opcjonalnie):**
   Aby bot działał 24/7 na serwerze, zaleca się użycie Docker Compose lub stworzenie usługi systemd.

## 🐳 Wdrożenie Docker (Zalecane na Linux)

1. **Uruchomienie za pomocą Docker Compose:**
   ```bash
   docker compose up -d
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
