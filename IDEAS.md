# Bot Musicka - Analiza i Pomysły v2.1

## ✅ v2.1 Naprawy (4 maja 2026)

### Problem 1: YouTube Format Not Available
- **Błąd:** `Requested format is not available`
- **Rozwiązanie v2.1:**
  1. Multi-format fallback (m4a → webm → mp4 → null)
  2. Invidious API jako backup dla samego URL
  3. Ręczne szukanie w formats array

### Problem 2: Cookies wymagane
- **Błąd:** `Sign in to confirm you're not a bot`
- **Rozwiązanie:** Invidious API nie wymaga cookies

---

## 📋 Stan v2.1 (4 maja 2026)

### ✅ Działające:
- Radio (stacje z API)
- Kolejka utworów
- Komendy: /play, /skip, /stop, /radio, /queue, /disconnect
- Auto-leave gdy bot sam na kanale
- YouTube (teraz z fallback)
- Spotify (przez oEmbed → YouTube search)

### 🔧 Do testów:
- Czy Invidious działa na VPS

---

## 💡 Pomysły na v2.2

1. **Interactive Search:**
   - Pokaż 5 wyników z YouTube
   - User wybiera numerem (1-5)

2. **Audio Filtry:**
   - bassboost, nightcore
   - przez ffmpeg -af filters

3. **Cache URL:**
   - Zapisuj działające URL do pliku
   - Odświeżaj co 24h

4. **Dashboard:**
   - HTTP endpoint z statystykami

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