# Analiza Kodu i Propozycje Update'ów - Bot Musicka

## 🆘 Critical Bugs Fixed (v1.3.0 patch2 - 27 kwietnia 2026 - 07:30 UTC)

### Issue 1: `yt-dlp-youtube-oauth2` PLUGIN FORCUJE OAUTH2
*   **Przyczyna:** `yt-dlp-youtube-oauth2` plugin w requirements.txt wymuszał OAuth2
*   **Error:** `[youtube+oauth2] HTTP Error 400 / Sign in to confirm you're not a bot`
*   **Fix:** ✅ **USUNIĘTY** plugin z requirements.txt - teraz yt-dlp używa web_embedded
*   **Impact:** KRYTYCZE - to był ROOT CAUSE całego problemu!

### Issue 2: Fallback Search Zwraca Empty Entries
*   **Przyczyna:** `extract_flat="in_playlist"` nie działa z ytsearch
*   **Fix:** ✅ Zmieniono na `extract_flat=False` + `playlistend=5` dla lepszych wyników
*   **Fix:** ✅ Fallback search teraz prawidłowo ekstrahuje query z URL

### Issue 3: Niedostateczny Logging
*   **Przyczyna:** Nie można było widzieć gdzie się łamie
*   **Fix:** ✅ DODANE [get_info], [from_url], [/play] prefixes w logach
*   **Fix:** ✅ Logowanie KAŻDEGO kroku w exception handlers
*   **Impact:** Teraz logi będą jasne i diagnozowalne

### Issue 4: Brak Timeout'u w yt-dlp
*   **Przyczyna:** yt-dlp mogł wisieć na YouTube
*   **Fix:** ✅ Dodano `socket_timeout: 30` i User-Agent header

### Przed:
```
[youtube+oauth2] HTTP Error 400 (PLUGIN wymuszał OAuth2)
✅ /play: 0 wpisów znaleźliśmy (empty results)
Brak loggingu gdzie się łamie
```

### Teraz:
```
✅ web_embedded client (PLUGIN USUNIĘTY)
✅ [get_info PRIMARY SUCCESS] Got data with entries count: 5
✅ [/play] Entries count: 5
✅ Każdy krok zalogowany - jasna diagnostyka
```

---

## 🔍 Analiza Błędów i Ryzyk (Code Audit)

### 1. Brak `cookies.txt` w repozytorium
*   **Ryzyko:** `music_handler.py` wymaga pliku `cookies.txt` do omijania blokad YouTube.
*   **Status:** ✅ Wdrożono walidację przy starcie i logowanie statusu w `main.py`.

### 2. Wycieki pamięci / zasobów (FFmpeg)
*   **Ryzyko:** `discord.FFmpegPCMAudio` bywa problematyczny pod kątem zamykania procesów.
*   **Status:** ✅ Wdrożono `on_voice_state_update` (Auto-Leave), który czyści zasoby, gdy bot zostaje sam.

### 3. Obsługa Spotify
*   **Ryzyko:** Nie można pobrać metadanych (DRM protection).
*   **Status:** ✅ Zmieniłem strategię – teraz szukamy na YouTube zamiast pobierać metadane. Spotify track → YouTube search. Spotify playlist → Dummy entries z wyszukiwaniem.

### 4. Błędy sieciowe (Radio)
*   **Ryzyko:** Linki radiowe mogą wygasnąć.
*   **Status:** ✅ Wdrożono obsługę wyjątków w komendzie `/radio` oraz dynamiczne budowanie URL dla OpenFM.

---

## 💡 Pomysły na Update (Roadmap 2.0)

### Poziom: Stabilność (Must-have)
1.  **System Auto-Reconnect:** ✅ Wdrożono przez parametry `-reconnect` w FFmpeg.
2.  **Health Check dla Radia:** Skrypt sprawdzający dostępność stacji raz na 24h.
3.  **Auto-Leave:** ✅ Wdrożono. Bot wychodzi po opuszczeniu kanału przez ludzi.

### Poziom: Funkcjonalność (User Experience)
4.  **Komenda `/queue`:** ✅ Wdrożono. Wyświetla listę oczekujących utworów (pierwsze 10).
5.  **Komenda `/status`:** ✅ Wdrożono. Diagnostyka bota (Discord, Voice, Queue, Radio API, Ping).
6.  **Komenda `/test`:** ✅ Wdrożono. Test wszystkich komponentów (Bot, Discord.py, FFmpeg, Radio API, yt-dlp, Logging).
7.  **Pobieranie Utworów (Pre-buffering):** Szybsze startowanie piosenki (w planach).
8.  **System Ulubionych:** ✅ Wdrożono `/favorites` i `/favorite add` (v1.3.0).
9.  **Historia Słuchania:** ✅ Wdrożono `/history` (v1.3.0).
10. **Wyszukiwanie interaktywne:** `/search <fraza>` wyświetla 5 wyników jako przyciski.

### Poziom: Pro/Admin (Zarządzanie)
11. **Panel Webowy (Dashboard):** Prosty podgląd statystyk bota.
12. **Wsparcie dla Multi-Server:** ✅ Wdrożono pełną separację kolejek.
13. **Logs System:** ✅ Wdrożono `bot.log` przez moduł `logging`.
14. **Komenda `/mystats`:** ✅ Wdrożono statystyki użytkownika (v1.3.0).
15. **Komenda `/nowplaying`:** ✅ Wdrożono info o aktualnym utworze (v1.3.0).

---

## 🔥 Nowe Horyzonty (Roadmap 2.0 - "Advanced Features")

13. **System "DJ Role":** Ograniczenie komend skip/stop dla osób z konkretną rolą na Discordzie.
14. **Interaktywne Karty Utworów (Rich Embeds):** Wyświetlanie miniatury (thumbnail), czasu trwania i paska postępu w Embedzie.
15. **Filtry Audio (FFmpeg):** Komenda `/effect bassboost` lub `/effect nightcore`.
16. **System Lyrics:** Pobieranie tekstów piosenek przez API Genius/Musixmatch.
17. **Tryb AI DJ:** Automatyczne dodawanie piosenek do kolejki na podstawie "podobnych utworów" z YouTube, gdy kolejka się skończy.
18. **Wsparcie dla lokalnych plików:** Folder `/music` na VPS, z którego bot może puszczać muzykę offline.
19. **Wsparcie dla SoundCloud i Deezer:** Rozszerzenie źródeł muzyki poza YouTube/Spotify.

---
*Autor: GitHub Copilot (Gemini 3 Flash (Preview))*
*Data: 23 kwietnia 2026*
