# Analiza Kodu i Propozycje Update'ów - Bot Musicka

## 🔍 Analiza Błędów i Ryzyk (Code Audit)

### 1. Brak `cookies.txt` w repozytorium
*   **Ryzyko:** `music_handler.py` wymaga pliku `cookies.txt` do omijania blokad YouTube. Jeśli plik nie zostanie dostarczony ręcznie na serwer (nie powinien być w gicie), bot wyrzuci błąd przy próbie odtwarzania.
*   **Status:** Do sprawdzenia przy starcie (dodanie logu informacyjnego).

### 2. Wycieki pamięci / zasobów (FFmpeg)
*   **Ryzyko:** `discord.FFmpegPCMAudio` bywa problematyczny pod kątem zamykania procesów FFmpeg, jeśli bot zostanie wyrzucony z kanału siłowo.
*   **Poprawka:** Warto dodać zdarzenie `on_voice_state_update`, aby czyścić kolejkę i zatrzymywać proces, gdy bot zostaje sam na kanale.

### 3. Obsługa Spotify
*   **Ryzyko:** `yt-dlp` bez dodatkowych pluginów pobiera ze Spotify tylko link, a nie zawsze potrafi go przekonwertować na meta-wyszukiwanie w YouTube dla każdego utworu z listy.
*   **Poprawka:** Lepsza integracja z wyszukiwaniem tytułu piosenek ze Spotify w YouTube.

### 4. Błędy sieciowe (Radio)
*   **Ryzyko:** Linki radiowe mogą wygasnąć lub serwer może przestać odpowiadać. Bot w tej chwili nie informuje użytkownika o "martwym linku".

---

## 💡 Pomysły na Update (Roadmap 2.0)

### Poziom: Stabilność (Must-have)
1.  **System Auto-Reconnect:** Lepsza obsługa zerwanych połączeń głosowych.
2.  **Health Check dla Radia:** Skrypt sprawdzający dostępność wszystkich 11 stacji raz na 24h.
3.  **Auto-Leave:** Bot wychodzi z kanału po 5 minutach ciszy, aby oszczędzać zasoby serwera VPS.

### Poziom: Funkcjonalność (User Experience)
4.  **Komenda `/queue`:** Wyświetlanie aktualnej listy oczekujących utworów (teraz kolejka jest ukryta).
5.  **Pobieranie Utworów (Pre-buffering):** Szybsze startowanie piosenki dzięki buforowaniu następnego utworu w tle do pliku tymczasowego.
6.  **System Ulubionych:** Możliwość zapisania piosenki do prywatnej listy bota (`/fav add`).
7.  **Wyszukiwanie interaktywne:** `/search <fraza>` wyświetla 5 wyników jako przyciski (Buttons) na Discordzie.

### Poziom: Pro/Admin (Zarządzanie)
8.  **Panel Webowy (Dashboard):** Prosty podgląd statystyk bota (ile serwerów, co aktualnie gra).
9.  **Wsparcie dla Multi-Server:** Pełna separacja kolejek (obecnie `self.queue` jest słownikiem, co jest poprawne, ale wymaga testów pod dużym obciążeniem).
10. **Logs System:** Zapisywanie błędów do pliku `bot.log` zamiast tylko do konsoli (ułatwia debugowanie na Dockerze).

---
*Autor: GitHub Copilot (Gemini 3 Flash (Preview))*
*Data: 23 kwietnia 2026*
