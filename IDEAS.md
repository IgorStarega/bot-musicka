# Analiza Kodu i Propozycje Update'ów - Bot Musicka

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
8.  **System Ulubionych:** Możliwość zapisania piosenki do prywatnej listy bota (`/fav add`).
9.  **Wyszukiwanie interaktywne:** `/search <fraza>` wyświetla 5 wyników jako przyciski.

### Poziom: Pro/Admin (Zarządzanie)
10. **Panel Webowy (Dashboard):** Prosty podgląd statystyk bota.
11. **Wsparcie dla Multi-Server:** ✅ Wdrożono pełną separację kolejek.
12. **Logs System:** ✅ Wdrożono `bot.log` przez moduł `logging`.

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
