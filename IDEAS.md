# Analiza Kodu i Propozycje Update'ów - Bot Musicka

## 🔍 Analiza Błędów i Ryzyk (Code Audit)

### 1. Brak `cookies.txt` w repozytorium
*   **Ryzyko:** `music_handler.py` wymaga pliku `cookies.txt` do omijania blokad YouTube.
*   **Status:** ✅ Wdrożono walidację przy starcie i logowanie statusu w `main.py`.

### 2. Wycieki pamięci / zasobów (FFmpeg)
*   **Ryzyko:** `discord.FFmpegPCMAudio` bywa problematyczny pod kątem zamykania procesów.
*   **Status:** ✅ Wdrożono `on_voice_state_update` (Auto-Leave), który czyści zasoby, gdy bot zostaje sam.

### 3. Obsługa Spotify
*   **Ryzyko:** Nieprecyzyjne wyszukiwanie utworów.
*   **Status:** ✅ Poprawiono `get_info` w `music_handler.py` – teraz wyszukuje "Tytuł + Wykonawca".

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
4.  **Komenda `/queue`:** ✅ Wdrożono. Wyświetla listę oczekujących utworów.
5.  **Pobieranie Utworów (Pre-buffering):** Szybsze startowanie piosenki (w planach).
6.  **System Ulubionych:** Możliwość zapisania piosenki do prywatnej listy bota (`/fav add`).
7.  **Wyszukiwanie interaktywne:** `/search <fraza>` wyświetla 5 wyników jako przyciski.

### Poziom: Pro/Admin (Zarządzanie)
8.  **Panel Webowy (Dashboard):** Prosty podgląd statystyk bota.
9.  **Wsparcie dla Multi-Server:** ✅ Wdrożono pełną separację kolejek.
10. **Logs System:** ✅ Wdrożono `bot.log` przez moduł `logging`.

---

## 🔥 Nowe Horyzonty (Roadmap 3.0 - "User Engagement")

11. **System "DJ Role":** Ograniczenie komend skip/stop dla osób z konkretną rolą na Discordzie.
12. **Interaktywne Karty Utworów:** Wyświetlanie miniatury (thumbnail), czasu trwania i paska postępu w Embedzie.
13. **Filtry Audio (FFmpeg):** Komenda `/effect bassboost` lub `/effect nightcore`.
14. **System Lyrics:** Pobieranie tekstów piosenek przez API Genius/Musixmatch.
15. **Tryb AI DJ:** Automatyczne dodawanie piosenek do kolejki na podstawie "podobnych utworów" z YouTube, gdy kolejka się skończy.
16. **Wsparcie dla lokalnych plików:** Folder `/music` na VPS, z którego bot może puszczać muzykę offline.

---
*Autor: GitHub Copilot (Gemini 3 Flash (Preview))*
*Data: 23 kwietnia 2026*
