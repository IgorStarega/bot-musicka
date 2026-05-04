# Bot Musicka - Analiza i Pomysły v2.0

## 🔴 KRITYCZNE Błędy (naprawione v2.0 - 4 maja 2026)

### Problem 1: YouTube Format Not Available
- **Błąd:** `Requested format is not available. Use --list-formats`
- **Przyczyna:** `bestaudio/best` nie działa dla wielu filmów na VPS
- **Rozwiązanie v2.0:** Używamy `extract_info(download=False)` + `formats` → szukamy URL ręcznie

### Problem 2: None w Entries
- **Błąd:** `entries[0] is NoneType`
- **Przyczyna:** yt-dlp zwraca listę z elementami `None`
- **Rozwiązanie:** Filtrujemy `None`: `entries = [e for e in data["entries"] if e is not None]`

### Problem 3: Brak URL w Entry
- **Błąd:** `Brak URL w wpisach: ...`
- **Przyczyna:** YouTube search zwraca tylko `id`, nie `url`
- **Rozwiązanie:** Konwertujemy `id` → `https://www.youtube.com/watch?v={id}`

### Problem 4: Spotify oEmbed → YouTube Search
- **Błąd:** Spotify title → ytsearch zwraca puste lub złe wyniki
- **Rozwiązanie:** Prosty `ytsearch1:{title}` z filtrowaniem None

---

## 📋 Stan v2.0 (4 maja 2026)

### ✅ Działające:
- Radio (stacje z API)
- Kolejka utworów
- Komendy: /play, /skip, /stop, /radio, /queue, /disconnect
- Auto-leave gdy bot sam na kanale

### ⚠️ Testowane:
- YouTube (formaty bywają niedostępne)
- Spotify ( przez oEmbed → YouTube search)

### 🔧 Do naprawy:
- Format YouTube - czasem nie działa bestaudio
- Lepszy fallback gdy format недоступный

---

## 💡 Pomysły na v2.1

1. **Multi-format fallback:**
   - Próbuj `bestaudio` → jak fail to `m4a` → jak fail to `webm` → jak fail to `direct URL`

2. **Cache URL:**
   - Zapisuj działające URL do pliku tymczasowego
   - Odświeżaj tylko co 24h

3. **Lepszy YouTube search:**
   - Użyj `youtube-search` API zamiast yt-dlp
   - Lub `yt-dlp "ytsearch10:{query}" --print url`

4. **Invidious instance:**
   - Użyj publicznej instancji Invidious zamiast YouTube
   - Np. `https://invidious.jingl.xyz/api/v1/videos/{id}`

5. **Pobieranie (offline mode):**
   - Pobieraj audio do `/tmp`
   - Odtwarzaj z pliku lokalnego

---

## 📊 Testowanie

### Test 1: YouTube
```
/play https://www.youtube.com/watch?v=VIDEO_ID
```

### Test 2: YouTube Search
```
/play nazwa piosenki
```

### Test 3: Spotify
```
/play https://open.spotify.com/track/TRACK_ID
```

### Test 4: Radio
```
/radio 130  (RMF FM)
```

---

*Ostatnia aktualizacja: 4 maja 2026*