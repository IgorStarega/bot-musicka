# Plan Rozwoju Bota Muzycznego - Bot Musicka

## Status Projektu: Produkcja (v1.3.0)

### Etapy:
1.  **[ZAKOŃCZONE]** Przygotowanie środowiska i bibliotek
2.  **[ZAKOŃCZONE]** Podstawowa konfiguracja bota (`/ping`)
3.  **[ZAKOŃCZONE]** System odtwarzania audio (FFmpeg i music_handler.py)
4.  **[ZAKOŃCZONE]** Integracja z YouTube i Spotify
5.  **[ZAKOŃCZONE]** System stacji radiowych
6.  **[ZAKOŃCZONE]** Komenda testowa `/test`
7.  **[ZAKOŃCZONE]** Migracja wrażliwych danych do `.env`
8.  **[ZAKOŃCZONE]** Konteneryzacja (Docker & Docker Compose)
9.  **[ZAKOŃCZONE]** CI/CD (GitHub Actions dla GHCR)
10. **[ZAKOŃCZONE]** Dokumentacja (README.md z instrukcją pod Linux)
11. **[ZAKOŃCZONE]** Optymalizacja pod serwer Linux (systemd service template)
12. **[ZAKOŃCZONE]** Poprawka błędu w składni GitHub Actions (referencja steps)
13. **[ZAKOŃCZONE]** Analiza kodu i poprawki stabilności (stop przed play, timeouty FFmpeg)
14. **[ZAKOŃCZONE]** Automatyczne dołączanie/przenoszenie bota przy komendach odtwarzania
15. **[ZAKOŃCZONE]** Rozwijana lista (Choices) dla komendy /radio
16. **[ZAKOŃCZONE]** Wdrożenie logowania do pliku `bot.log`
17. **[ZAKOŃCZONE]** System Auto-Leave (oszczędzanie zasobów VPS)
18. **[ZAKOŃCZONE]** Naprawa obsługi playlist i błędów NoneType
19. **[ZAKOŃCZONE]** Optymalizacja wyszukiwania Spotify (Tytuł + Wykonawca)
20. **[ZAKOŃCZONE]** Komenda `/queue` i ulepszona lista stacji radiowych

### Dodatkowe Milestones (v1.1.0 Extended):
21. **[ZAKOŃCZONE]** YouTube fallback na wyszukiwanie (152-18 unavailable videos)
22. **[ZAKOŃCZONE]** Spotify bez DRM - szukanie na YouTube zamiast pobierania metadanych
23. **[ZAKOŃCZONE]** Playlist YouTube z ignorowaniem błędów (ignorerrors=True)
24. **[ZAKOŃCZONE]** Komenda `/status` - diagnostyka bota
25. **[ZAKOŃCZONE]** Komenda `/test` - test komponentów
26. **[ZAKOŃCZONE]** Usuniętych zależności (spotipy) - v1.1.0+ nie potrzebuje
27. **[ZAKOŃCZONE]** Aktualizacja README.md o nowe komendy i strategie

### v1.3.0 Milestones (Social & Interactive):
28. **[ZAKOŃCZONE]** System storage (user_storage.py) - JSON-based persistent storage
29. **[ZAKOŃCZONE]** Komenda `/favorites` - wyświetl ulubione utwory
30. **[ZAKOŃCZONE]** Komenda `/history` - historia ostatnio granych utworów
31. **[ZAKOŃCZONE]** Komenda `/nowplaying` - info o aktualnym utworze
32. **[ZAKOŃCZONE]** Komenda `/mystats` - statystyki użytkownika z embedem
33. **[ZAKOŃCZONE]** Tracking skip'ów w statystykach
34. **[ZAKOŃCZONE]** Dodanie do historii automatycznie podczas odtwarzania

### v1.3.0 Hotfixes (27 kwietnia 2026):
35. **[ZAKOŃCZONE]** Fix: OAuth2 HTTP 400 - zmieniono na web_embedded client
36. **[ZAKOŃCZONE]** Fix: `get_info()` zwraca dict zamiast None (fallback na wyszukiwanie)
37. **[ZAKOŃCZONE]** Improvement: `/play` bezpieczna obsługa błędów z auto-fallback'iem
38. **[ZAKOŃCZONE - KRYTYCZNE]** Fix: USUNIĘTY `yt-dlp-youtube-oauth2` plugin - to wymuszało OAuth2!
39. **[ZAKOŃCZONE]** Fix: `extract_flat` w wyszukiwaniu - changed to False dla lepszych wyników
40. **[ZAKOŃCZONE]** Improvement: KOMPLETNY logging w get_info(), from_url(), /play z prefixes
41. **[ZAKOŃCZONE]** Improvement: Dodany socket_timeout i User-Agent do yt-dlp options

### v1.4.0 Milestones (Commands & Fixes - 27 kwietnia 2026):
42. **[ZAKOŃCZONE]** Fix: `/nowplaying` - teraz pokazuje prawdziwy tytuł i URL aktualnego utworu
43. **[ZAKOŃCZONE]** Fix: `/favorite add/remove` - działa przez `current_track` tracking
44. **[ZAKOŃCZONE]** FEAT: `/pause` - wstrzymanie odtwarzania
45. **[ZAKOŃCZONE]** FEAT: `/resume` - wznowienie odtwarzania po pauzie
46. **[ZAKOŃCZONE]** FEAT: `/volume [0-100]` - zmiana głośności
47. **[ZAKOŃCZONE]** Improvement: `from_url()` - `title_hint` param dla lepszego fallback search
48. **[ZAKOŃCZONE]** Improvement: Tracking `current_track` per guild w MusicBot

### Dane bota:
- **Wersja:** 1.4.0 (Commands & Fixes)
- **Platforma:** Linux / Docker
- **Typ:** Zaawansowany Bot Muzyczny
- **Status:** Production-Ready ✅ (pause/resume/volume, nowplaying fixed, favorite fixed)

---
Ostatnia aktualizacja: 27 kwietnia 2026 (v1.4.0 - Commands & Fixes)
