# Bot Musicka - Plan Rozwoju

## 📊 Historia Wersji

### v2.1 (4 maja 2026) - Stabilność YouTube
- ✅ Multi-format fallback (m4a → webm → mp4 → null)
- ✅ Invidious API jako backup
- ✅ Lepszy error handling
- ✅ Debug logi

### v2.0 (4 maja 2026) - Naprawa
- ✅ Przepisany music_handler.py (prostszy kod)
- ✅ Przepisany main.py (prostszy kod)
- ✅ Filtruj None z entries
- ✅ Konwertuj id → url

---

## 🎯 v2.2 Priorytety

### 1. FEAT: Interactive Search
- Pokaż 5 wyników z YouTube
- User wybiera numerem

### 2. FEAT: Audio Filtry
- bassboost, nightcore
- przez ffmpeg filters

### 3. IMPROVE: Cache
- Cache działających URL
- Odświeżaj co 24h

---

## 🧪 Testy Przed Wydaniem v2.2

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

## 📦 Przyszłe Funkcje (v2.3+)

1. **Playlist YouTube** - obsługa pełnych playlist
2. **Dashboard web** - statystyki przez HTTP

---

*Ostatnia aktualizacja: 4 maja 2026*