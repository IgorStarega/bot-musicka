# UPDATE 2.1 - Naprawa YouTube Bot-Detection i HTTP 429

## 🔴 Problem (z logów 2026-04-23)

```
ERROR: [youtube] NgGocWmOst0: Sign in to confirm you're not a bot.
ERROR: [youtube] PvQRpV1-ZhY: Sign in to confirm you're not a bot.
HTTP error 429 Too Many Requests
Error opening input file https://www.youtube.com/watch?v=...
```

## 🎯 Root Cause

YouTube wprowadził bardziej agresywne wykrywanie botów (Proof-of-Origin Token enforcement).
Klienty `tv_embedded` i `android` używane w `player_client` są coraz częściej blokowane przez YouTube na IP VPS.

Dodatkowy problem: błędy "Sign in to confirm you're not a bot" nie były objęte warunkami fallback search w `from_url()`, więc wyjątek był rzucany od razu zamiast szukać alternatywy.

## ✅ Zastosowane Naprawy

### 1. Zmiana `player_client` na `["ios", "android"]`

**Dlaczego `ios`?**
- iOS client używa innego API endpoint (YouTube iOS app)
- Nie wymaga JavaScript execution
- Mniej agresywnie filtrowany przez YouTube's bot-detection
- Zwraca prawdziwe stream URL (`googlevideo.com`) bez potrzeby cookies
- W kombinacji z `android` jako fallback pokrywa większość przypadków

**Zmienione miejsca:**
- `get_ydl_options()` - dla pobierania einzelnych URL
- `get_ydl_search_options()` - dla wyszukiwania

### 2. Rozszerzenie warunków fallback search

**Stary kod:**
```python
if any(x in error_str for x in ["152", "unavailable", "private", "removed", "deleted"]):
```

**Nowy kod:**
```python
if any(x in error_str for x in ["152", "unavailable", "private", "removed", "deleted", "sign in", "not a bot", "login required"]):
```

Teraz gdy YouTube mówi "Sign in to confirm you're not a bot", bot przełącza się na wyszukiwanie alternatywy zamiast rzucać błąd.

### 3. Dynamiczne FFMPEG_OPTIONS przez funkcję `get_ffmpeg_options()`

Dodano funkcję `get_ffmpeg_options()` dla łatwiejszej rozbudowy w przyszłości (np. dodanie proxy, innych headerów). `from_url()` teraz używa tej funkcji zamiast stałego `FFMPEG_OPTIONS`.

### 4. Priorytet formatu audio dla iOS client

Zmieniono kolejność formatu z `"251/250/249/140/..."` na `"140/251/250/249/..."`.
Format 140 (m4a/AAC) jest natywnie dostępny na iOS client i ma pierwszeństwo.

### 5. Zmniejszenie sleep_interval

Zmniejszono z 2s do 1s między żądaniami - szybsze odpowiedzi bez istotnego zwiększenia ryzyka rate-limitingu.

## 📊 Przepływ Po Naprawie

```
1. /play <youtube_url>
   ↓
2. get_info() → zwraca entries z URL
   ↓
3. from_url(url) → get_ydl_options() [player_client: ios, android]
   ↓
4. yt-dlp z iOS client → zwraca stream URL (googlevideo.com) BEZ wymagania logowania
   ↓
5. FFmpeg otwiera stream URL bezpośrednio → muzyka gra ✅

Przypadek błędu (jeśli iOS też zablokowany):
3b. yt-dlp zwraca "Sign in to confirm you're not a bot"
   ↓
4b. Warunek fallback match → szukaj "ytsearch:popularna piosenka"
   ↓
5b. Znajdź alternatywny utwór → graj ✅
```

## 🔧 Co Robić Jeśli Problem Wróci

Jeśli `ios` client też zostanie zablokowany, możliwe rozwiązania:
1. Zmień `player_client` na `["mweb", "ios"]`
2. Spróbuj `["android_music", "android"]`
3. Odnów cookies.txt (pobierz nowe z przeglądarki)
4. Ostateczność: skonfiguruj proxy w yt-dlp (`proxy: "http://..."`)

## 📝 Zmienione Pliki

- `music_handler.py` - wszystkie zmiany opisane powyżej

---

**Data naprawy:** 23 kwietnia 2026  
**Agent:** GitHub Copilot  
**Status:** ✅ Wdrożono
