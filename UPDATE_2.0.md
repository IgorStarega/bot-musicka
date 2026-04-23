# Music Bot v2.0 - Instrukcje Aktualizacji

## Co się zmieniło?

### 🔧 music_handler.py - Kompletne przepisanie
- **Usuniętych próby pobierania metadanych Spotify (DRM blocker)** - teraz szukamy na YouTube bez DRM
- **Fallback dla YouTube 152-18** - jeśli film niedostępny, szukamy alternatywy automatycznie
- **Playlist YouTube z ignorowaniem błędów** - teraz `ignoreerrors=True` dla playlisty
- **Uproszczone wyszukiwanie** - dla Spotify i YouTube niedostępnych

### 🎯 Strategia nowa
```
Spotify → Szukaj na YouTube (bez DRM)
YouTube 152-18 → Fallback na wyszukiwanie
YouTube Playlist → Pobierz + Ignoruj błędy
```

### ✂️ Usunięte zależności
- **spotipy** - nie potrzebujemy (DRM protection)

### 📝 main.py - Uproszczenia
- Lepsze komunikaty z emoji
- Czytelne logowanie
- Szybsze odpowiedzi

## Aktualizacja na VPS

```bash
cd ~/docker/bot-musicka

# 1. Pull latest (jeśli na git)
git pull origin main

# 2. Restart
docker compose down
docker compose up -d --build

# 3. Czekaj 30s
sleep 30

# 4. Sprawdzaj logi
docker compose logs -f
```

## Test polecenia

Po starcie bot powinien wyświetlić:
```
✅ Zsynchronizowano komendy slash dla Miusnigg#9157
Zalogowano jako Miusnigg#9157
```

Testuj:
```
/play https://www.youtube.com/watch?v=xxx          (YouTube single)
/play https://www.youtube.com/playlist?list=xxx    (YouTube playlist)
/play https://open.spotify.com/track/xxx           (Spotify - konwertuje)
/play popular music                                 (Wyszukiwanie)
```

## Oczekiwane logi

- YouTube Single: 🎬 YouTube single - pobieram...
- YouTube Playlist: 📺 YouTube playlist - pobieram wpisy...
- Spotify Track: 🎵 Spotify link - szukam na YouTube...
- Film niedostępny: Film niedostępny na tym IP, szukam alternatywy...

## Znane ograniczenia

✅ **Rozwiązane:**
- Spotify DRM - teraz szukamy na YouTube
- YouTube 152-18 - fallback na wyszukiwanie
- Playlist YouTube - ignorujemy błędy

⚠️ **Może nie zawsze zadziałać:**
- Jeśli YouTube całkowicie zablokuje IP VPS (mało prawdopodobne z web_embedded)
- Wyszukiwanie zwróci "popular music" zamiast konkretnego utworu (ale gram COŚ)

## Co dalej?

Bot jest gotowy do **24/7 produkcji**. Monitoruj `bot.log` pod kątem błędów.
