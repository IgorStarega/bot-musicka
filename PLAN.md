# Bot Musicka - Plan Rozwoju

## 📊 Historia Wersji

### v1.5.0 (27 kwietnia 2026) - Optymalizacja
- ✅ /disconnect komenda
- ✅ Kolejka trzyma {"url", "title"} zamiast gołych URL
- ✅ Lepsze logi DEBUG
- ✅ /status pokazuje prawdziwy stan

### v2.0 (4 maja 2026) - Naprawa
- ✅ Przepisany music_handler.py (prostszy kod)
- ✅ Przepisany main.py (prostszy kod)
- ✅ Filtruj None z entries
- ✅ Konwertuj id → url
- ⚠️ YouTube format - nadal bywa problem

### v2.1 (W planach) - Stabilność YouTube

---

## 🎯 v2.1 Priorytety

### 1. FIX: YouTube Format Problem [KRYTYCZNE]
- **Problem:** `Requested format is not available`
- **Rozwiązania do testów:**
  - a) `format: "bestaudio/[Protocol=http*m4a]/bestaudio/best"`
  - b) Użyj Invidious API zamiast yt-dlp
  - c) Pobieraj audio do /tmp potem odtwarzaj

### 2. FEAT: Lepszy Fallback
- Gdy główny format fail → próbuj alternatywny
- Loguj każdą próbę by wiedzieć co działa

### 3. IMPROVE: Spotify
- Lepsze wyszukiwanie YouTube z tytułu Spotify
- Cache результатов

---

## 🧪 Testy Przed Wydaniem v2.1

```bash
# Testuj różne formaty YouTube
/play https://www.youtube.com/watch?v=VIDEO_ID_1
/play https://www.youtube.com/watch?v=VIDEO_ID_2
/play nazwa_piosenki

# Testuj Spotify  
/play https://open.spotify.com/track/ID

# Testuj Radio
/list_radio
/radio 130
```

---

## 📦 Przyszłe Funkcje (v2.2+)

1. **Playlist YouTube** - obsługa pełnych playlist
2. **Search interaktywny** - pokaż 5 wyników, wybierz
3. **Audio filtry** - bassboost, nightcore
4. **Dashboard web** - statystyki przez HTTP

---

*Ostatnia aktualizacja: 4 maja 2026*