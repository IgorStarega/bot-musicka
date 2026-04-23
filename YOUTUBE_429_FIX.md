# YouTube HTTP 429 "Too Many Requests" - Root Cause & Solution

## 🔴 Problem

Bot nie może odtwarzać YouTube video. Logi pokazują:
```
HTTP error 429 Too Many Requests
Error opening input file https://www.youtube.com/watch?v=...
```

## 🎯 Root Cause (Główna Przyczyna)

**yt-dlp zwraca video page URL zamiast stream URL:**
- `https://www.youtube.com/watch?v=PvQRpV1-ZhY` ← Video page (HTML), nie stream!
- FFmpeg nie może otworzyć HTML stronę
- YouTube zwraca HTTP 429 bo FFmpeg wygląda jak bot

## 🔍 Diagnostyka

```python
# Logi pokazują:
→ Formats dostępne: 0 szt.    # ← PROBLEM! YouTube nie daje formatów
→ formats dostępne: False     # ← YouTube blokuje dostęp do stream info

# Przyczyna:
- extract_flat: 'in_playlist' zwraca TYLKO video page URL
- Bez extract_flat → rate limit YouTube (152-18)
```

## ✅ Rozwiązanie - FFmpeg YouTube Parser

**FFmpeg ma wbudowany YouTube parser.** Pozwól mu parsować URL bezpośrednio:

```python
FFMPEG_OPTIONS = {
    "before_options": "-user_agent \"Mozilla/5.0...\" -cookies config/cookies.txt",
    # ↑ Dodaj cookies.txt - YouTube wymaga
}

# W music_handler.py:
filename = data.get("url")  # watch?v=PvQRpV1-ZhY

if "watch?v=" in filename:
    # FFmpeg sparsuje to automatycznie
    return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)
```

**Jak to działa:**
1. yt-dlp zwraca video page URL
2. FFmpeg otwiera URL
3. FFmpeg wbudowany parser pobiera stream
4. Audio jest odtwarzane

## 📋 Opcje FFmpeg (Ważne!)

```python
FFMPEG_OPTIONS = {
    "before_options": 
        "-user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64)\" "
        "-headers \"User-Agent: Mozilla/5.0\\r\\n\" "
        "-reconnect 1 -reconnect_streamed 1 "
        "-reconnect_delay_max 5 "
        "-timeout 30000000 "
        "-cookies config/cookies.txt",  # ← Cookies z ciasteczkami
    "options": "-vn -dn -sn -ignore_unknown -probesize 32k -analyzeduration 0"
}
```

**Wyjaśnienie:**
- `-cookies config/cookies.txt` - YouTube wymaga cookies by parsować video
- `-user_agent` - Musi być realny User-Agent
- `-reconnect` - Reconnect na timeout

## 🎬 Format Selection Problem

**NIE RÓB:**
```python
"format": "best"  # ← Nie daje stream URL
"extract_flat": "in_playlist"  # ← Zwraca tylko video page URL
```

**RÓB:**
- Pozwól yt-dlp zwrócić video page URL
- Niech FFmpeg to parsuje bezpośrednio
- FFmpeg ma built-in YouTube parser

## 🚨 Jeśli HTTP 429 Dalej Się Pojawia

**Przyczyna:** YouTube blokuje VPS IP na HTTP level

**Rozwiązania (w kolejności):**

1. **Cookies + User-Agent** (Commit 07e4c3a)
   - Dodaj `-cookies config/cookies.txt` do FFmpeg options
   - Dodaj prawidłowy User-Agent header

2. **Zmień player_client** w yt-dlp options:
   ```python
   "extractor_args": {
       "youtube": {
           "player_client": ["tv_embedded", "web"],  # Spróbuj inny klient
       }
   }
   ```

3. **Timeout zwiększony:**
   ```python
   "socket_timeout": 120,
   "http_timeout": 30,
   ```

4. **Jeśli nic nie działa:** IP blacklist
   - YouTube zablokował VPS IP całkowicie
   - Rozwiązanie: Proxy service (OVH, ProxyScrape, itp.)

## 📝 Kod Solution (Commit c70fd19 + 07e4c3a)

```python
# music_handler.py - from_url()

# 1. Pobierz video info z yt-dlp
data = await yt_dlp.YoutubeDL(opts).extract_info(url, download=not stream)

# 2. Dostań URL (może być video page URL)
filename = data.get("url")  # watch?v=...

# 3. FFmpeg sparsuje to bezpośrednio
return cls(
    discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS),  # ← FFmpeg parser
    data=data
)
```

## 🔧 Jeśli Znowu Się Pojawi

Szukaj w logach:
```
HTTP error 429       ← Rate limiting
Format dostępne: 0   ← YouTube blokuje dostęp do stream info
```

**Próbuj:**
1. Zmień `player_client` na `["tv_embedded"]`
2. Zwiększ timeout w yt-dlp
3. Sprawdź czy cookies.txt istnieje
4. Jeśli nic: Proxy

## 📌 Kluczowe Learning

- **yt-dlp nie zawsze daje stream URL** - zwraca video page URL
- **FFmpeg może parsować YouTube bezpośrednio** - wbudowany parser
- **Cookies są ważne** - YouTube wymaga na HTTP level
- **IP blacklist to problem** - wtedy trzeba proxy

---

**Status:** ✅ Rozwiązane w commit `07e4c3a`  
**Data:** 23.04.2026  
**Agent:** GitHub Copilot
