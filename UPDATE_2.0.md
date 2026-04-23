# Music Bot v1.1.0+ - Instrukcje Aktualizacji (Extended Features)

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

---

# 📈 Plany Rozwoju Bot-Musicka

## Roadmap 1.2.0 - "Stabilizacja & Polish" (Q1 2026)

### 🔧 Ulepszenia Techniczne
- [ ] **Metrics & Monitoring** - Dashboard z metrykami (uptime, tracks played, errors)
- [ ] **Advanced Logging** - Rotacja logów, archiw logów starszych niż 7 dni
- [ ] **Health Check API** - `/health` endpoint do monitorowania stanu bota
- [ ] **Graceful Shutdown** - Poprawne czyszczenie zasobów przy restarcie
- [ ] **Connection Pooling** - Ponowne użycie połączeń dla Radio API

### 🎤 Nowe Komendy
- [ ] `/nowplaying` - Pokazuje info o aktualnie grającym utworze (tytuł, czas, URL)
- [ ] `/pause` / `/resume` - Wznowienie i pauza audio
- [ ] `/volume [0-100]` - Zmiana głośności bota
- [ ] `/loop [track|playlist|off]` - Pętla odtwarzania
- [ ] `/shuffle` - Tasowanie kolejki

### 📊 Diagnostyka
- [ ] `/debug` - Rozszerzona diagnostyka (memory usage, CPU, threads)
- [ ] `/logs [count]` - Wyświetl ostatnie N linii z `bot.log`
- [ ] `/info [track_id]` - Info o utworze (yt-dlp metadata)

---

## Roadmap 1.3.0 - "Social & Interactive" (Q2 2026)

### 🎭 Interaktywne Embedy
- [ ] **Rich Track Cards** - Embed z miniaturą YouTube, czasem trwania, paska postępu
- [ ] **Queue Preview** - Embed wyświetlający aktualną kolejkę w GUI
- [ ] **Now Playing Button** - Przycisk "👍 Polub" / "👎 Nie polub" dla utworu

### 💾 Ulubione & Historia
- [ ] `/favorite add` - Dodaj aktualnie grający utwór do ulubionych
- [ ] `/favorites list` - Lista ulubionych (offline, w pamięci bota)
- [ ] `/history` - Historia 20 ostatnio granych utworów
- [ ] `/recent-searches` - Ostatnie wyszukiwania użytkownika

### 👥 Społeczność
- [ ] **Reactions** - 🎵 Emoji na wiadomościach bota do quick commands
- [ ] **Shared Queue** - Widoczna dla wszystkich na kanale kolejka + komenda do skonfigurowania kanału wyświetlania kolejki
- [ ] **User Stats** - `/mystats` - Ilość piosenek, favorite genre itp.

---

## Roadmap 2.0 - "Advanced Features" (Q3 2026)

### Struktura plików
- [] kompletna przebudowa struktury tak aby najważniejsze rzeczy z kodu były w odzielnych plikach, przejrzystość kodu oraz porządek z dokumentacją, niepotrzebne pliki do usunięcia tak samo stare pliki oraz napisanie kodu od nowa zachowując obecną funkcjonalność bota ale zapeniająca przejrzystość w kodzie i logach. Na koniec usunięcie starych komend i napisanie ich od nowa tak aby wyglądały na nowocześniejsze oraz optymalizacja bota.

### 🎚️ Audio Effects & Processing
- [ ] `/effect bassboost` - Wzmocnienie basów
- [ ] `/effect nightcore` - Efekt nightcore (tempo +20%, pitch +5%)
- [ ] `/effect slowmo` - Spowolnienie (tempo -20%)
- [ ] `/effect reverb` - Reverb effect
- [ ] `/effect tremolo` - Efekt tremolo

### 🔄 Smart Queue Management
- [ ] `/recommend [artist|genre]` - AI sugestie utworów do kolejki
- [ ] `/autoplay` - Automatyczne dodawanie podobnych utworów po skończeniu kolejki
- [ ] `/smart-shuffle` - Tasowanie zachowujące tempo i gatunek

### 🌐 Rozszerzone Źródła Muzyki
- [ ] **SoundCloud** - Obsługa linków SC (yt-dlp już wspiera)
- [ ] **Deezer** - Integracja z Deezer API
- [ ] **Tidal** - Wsparcie dla Tidal (HiFi audio)
- [ ] **Local Files** - Odtwarzanie plików mp3 z `/music` folderu na VPS

### 📝 Lyrics & Metadata
- [ ] `/lyrics` - Wyświetl tekst aktualnej piosenki (Genius API)
- [ ] `/artistinfo` - Info o artyście (z Spotify API, bez pobierania audio)
- [ ] `/chartbeat` - Popularne utwory tego tygodnia

---

## Roadmap 2.5 - "Admin & Management" (Q4 2026)

### 👮 Role-Based Access Control
- [ ] **DJ Role** - Użytkownicy z rolą `DJ` mogą skipować/stopować dla wszystkich
- [ ] **Admin Commands** - `/admin restrict-queue-size [N]` - Limit kolejki
- [ ] **Mod Commands** - `/mod freeze-queue` - Zablokuj dodawanie nowych piosenek
- [ ] **Whitelist/Blacklist** - `/admin blacklist-artist [name]` - Zabanuj artystę

### 📊 Dashboard & Analytics
- [ ] **Web Dashboard** - Prosty panel pod `localhost:8080` z statystykami
- [ ] **DB Storage** - SQLite do zapisywania statystyk (ulubionych, historii, stats)
- [ ] **Export Stats** - `/stats export` - CSV z danymi za ostatnie 30 dni

### ⚙️ Konfiguracja Per-Guild
- [ ] `/config max-queue-size` - Ustaw limit kolejki dla serwera
- [ ] `/config welcome-message` - Własna wiadomość powitalną
- [ ] `/config announcements` - Czy bot ogłasza nowe utwory
- [ ] `/config language` - Zmień język bot-a (PL/EN/DE/FR)

---

## Roadmap 3.0 - "AI & Automation" (2027)

### 🤖 AI DJ Mode
- [ ] **ML-Based Recommendations** - Trenowanie modelu na historii użytkownika
- [ ] **Mood Detection** - Bot automatycznie wybiera muzykę na osnowie "moody" (happy, sad, epic, chill)
- [ ] **Auto DJ** - Włącz `/autoplay` i bot ciągle dodaje similar tracks
- [ ] **Playlist Generator** - `/generate-playlist [mood] [duration]` - Wygeneruj playlistę

### 🔊 Advanced Audio
- [ ] **3D Audio / Spatial** - Implementacja Dolby Atmos (discord.py może nie wspierać)
- [ ] **Real-Time Equalizer** - 10-band EQ z `/eq preset`
- [ ] **Dynamic Normalization** - Wyrównywanie głośności między utworami
- [ ] **Beat Sync Visualizer** - ASCII art synced do beat'u

### 🌍 Multilingual Support
- [ ] [ ] Wszystkie komendy w PL, EN, DE, FR, ES, IT
- [ ] **Translations** - i18n system
- [ ] **Regional Music Charts** - Domyślna playlista na bazie lokalizacji

---

## Techniczne Ulepszenia (All Versions)

### Performance & Stability
- [ ] **Async Improvements** - Całkowity refactor na asyncio bez `.run_in_executor()`
- [ ] **Memory Optimization** - Zmniejszenie footprinta (cache invalidation)
- [ ] **DB Connection Pool** - Redis dla cache'u (URL cache, radio stations cache)
- [ ] **Rate Limiting** - Ochrona przed spam'em komend
- [ ] **Circuit Breaker** - Ochrona Radio API przed permanent failures

### Testing & QA
- [ ] **Unit Tests** - pytest dla `music_handler.py`, `config.py`
- [ ] **Integration Tests** - Testy Discord API interactions
- [ ] **Load Testing** - Symulacja 10+ guildów jednocześnie
- [ ] **CI/CD Pipeline** - GitHub Actions do automaty testów

### DevOps & Deployment
- [ ] **Kubernetes Support** - Helm charts dla K8s
- [ ] **Multi-Region Deployment** - Bot na wieluset serwerach (load balancing)
- [ ] **Blue-Green Deployment** - Zero-downtime updates
- [ ] **Monitoring Stack** - Prometheus + Grafana
- [ ] **Error Tracking** - Sentry integration

---

## Feature Priority Matrix

```
HIGH IMPACT, LOW EFFORT:
✅ /nowplaying, /pause, /volume
✅ /favorite add/list
✅ Rich embeds

MEDIUM IMPACT, MEDIUM EFFORT:
- Audio Effects
- Smart Queue
- Admin Commands
- Web Dashboard

HIGH IMPACT, HIGH EFFORT:
- AI DJ Mode
- Advanced Audio
- Multi-language
- Kubernetes
```

---

## Bug Tracker & Known Issues

### Current Known Issues (v1.1.0)
- ⚠️ FFmpeg timeout na VPS bez wystarczającego throughput
- ⚠️ Czasami Radio API timeout (fallback do hardcoded stacji)
- ⚠️ Długie playlisty YouTube mogą nie załadować całkowicie
- ⚠️ Brak support dla encrypted YouTube streams (premium content)

### Planned Fixes
- [ ] Implement retry logic z exponential backoff dla Radio API
- [ ] Async playlist loading (stream entries zamiast load all)
- [ ] WebRTC connection pooling dla Voice Gateway
- [ ] Graceful handling encrypted content (skip z info)

---

## Contributing Guidelines

Każdy agent chcący dodać nową funkcję powinien:

1. **Wybrać z Roadmap** - Ustalone feature z powyższych planów
2. **Utworzyć branch** - `feature/nowplaying` lub `fix/radio-timeout`
3. **Implement & Test** - Kod + testy w Docker
4. **Update docs** - README, AGENTS.md, PLAN.md
5. **Pull Request** - Z opisem i linkami do issue'ów

---

## Kontakt & Feedback

- 📝 **Issues:** Zgłaszaj problemy w `bot.log` + opisz w README
- 💡 **Ideas:** Nowe feature ideas do `IDEAS.md`
- 🐛 **Bugs:** Potwierdź czy reprodukowalny, potem raportuj

---

**Ostatnia aktualizacja:** 23 kwietnia 2026  
**Maintain By:** GitHub Copilot + Community  
**License:** MIT (jeśli będzie)
