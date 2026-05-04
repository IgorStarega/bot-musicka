# 🎵 Bot Musicka v2.0

Bot muzyczny na Discord - YouTube, Spotify, Radio.

**Wersja:** 2.0 (Naprawa - 4 maja 2026)
**Język:** Python 3.11+
**Technologia:** discord.py, yt-dlp, FFmpeg
**Status:** ⚠️ Testowanie

## 🚀 Funkcje
- 📻 **Radio:** Stacje z API
- 📺 **YouTube:** Odtwarzanie (bywa problem z formatami)
- 🎵 **Spotify:** przez oEmbed → YouTube search
- 📋 **Kolejka:** widoczna lista utworów
- 🐚 **Slash Commands:** /play, /radio, /skip, /stop, /queue, /disconnect
- 🐳 **Docker:** Gotowe do VPS

## 💻 Uruchomienie

```bash
# 1. Skonfiguruj .env
echo DISCORD_TOKEN=TwójToken > .env

# 2. Uruchom
docker compose up -d --build

# 3. Logi
docker compose logs -f
```

## 📋 Komendy

| Komenda | Opis |
|--------|-----|
| `/play link` | Odtwórz z YouTube/Spotify |
| `/radio ID` | Odtwórz stację radiową |
| `/list_radio` | Lista stacji |
| `/queue` | Kolejka |
| `/skip` | Pomiń |
| `/stop` | Zatrzymaj |
| `/disconnect` | Odłącz bota |
| `/status` | Status bota |

## ⚠️ Znane Problemy

1. **YouTube format:** Czasem film nie ma `bestaudio`
   - Fallback: szuka innego formatu lub używa URL

2. **Spotify search:** Zależne od oEmbed API

## 📁 Struktura

- `main.py` - Główne komendy
- `music_handler.py` - yt-dlp / audio
- `config.py` - Radio API
- `user_storage.py` - Ulubione/historia

---

*Data: 4 maja 2026 | v2.0*