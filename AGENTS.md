# AGENTS.md - Wytyczne dla Agentów Edytujących Repo

## 📋 Cel dokumentu

Ten plik definiuje reguły, konwencje i procedury dla wszystkich agentów (w tym GitHub Copilot), które edytują kod w tym repozytorium. Każdy agent **MUSI** przestrzegać poniższych wytycznych.

---

## 🤖 Rola Agentów

### Główne obowiązki:
1. ✅ **Naprawiać błędy** - debugowanie i rozwiązywanie problemów
2. ✨ **Dodawać funkcje** - nowe komendy Discord, integracje
3. 🔧 **Refaktorować kod** - poprawa jakości, czytelności
4. 📚 **Dokumentować** - README, komentarze, instrukcje
5. 🚀 **Stabilizować** - error handling, logging, production-readiness

### Zakazy:
❌ Zmieniać strukturę projektu bez zgody użytkownika  
❌ Usuwać pliki bez uzasadnienia  
❌ Dodawać duże zależności bez omówienia  
❌ Commitować bez wiadomości  
❌ Testować na produkcji (VPS)

---

## 📁 Struktura Projektu - Nie Zmieniaj!

```
bot-musicka/
├── main.py                 # Discord bot core + all commands (v1.3.0: 13 komend)
├── music_handler.py        # yt-dlp integration + audio streaming
├── config.py               # Environment vars + Radio API
├── user_storage.py         # User data storage (v1.3.0: favorites, history, stats - JSON based)
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Multi-stage build
├── README.md               # User documentation
├── PLAN.md                 # Development roadmap
├── IDEAS.md                # Error analysis + feature ideas
├── UPDATE_*.md             # Version changelog
├── AGENTS.md               # This file
├── .env.example            # Env template
├── .gitignore              # Git rules
└── config/                 # Persistent files (cookies, user_data/)
    ├── cookies.txt         # YouTube cookies (ignored)
    └── user_data/          # User storage (favorites, history) - JSON files
        └── users.json      # All user data combined
```

**Reguła:** Nie dodawaj nowych plików bez dyskusji z użytkownikiem!

---

## 🎯 Konwencje Kodowania

### Python Style
- **Język:** Polish comments, English docstrings
- **Indentation:** 4 spaces
- **Linting:** Nie wymuszane, ale PEP8 mile widziane
- **Logging:** `logger.info()`, `logger.error()`, `logger.warning()`
- **Type hints:** Opcjonalne ale zalecane dla nowych funkcji

### Struktura Pliku - main.py
```
1. Imports
2. Logging setup
3. Bot init + intents
4. Utility functions (ensure_voice, update_status, etc.)
5. Event handlers (@bot.event)
6. Commands (@bot.tree.command) - sorted by name
7. Autocomplete functions
8. Main entry point (if __name__ == "__main__")
```

### Struktura Pliku - music_handler.py
```
1. Imports
2. Logging setup
3. FFMPEG_OPTIONS dict
4. URL detection functions (is_youtube_url, is_spotify_url, etc.)
5. get_ydl_options() function
6. YTDLSource class
   - __init__()
   - from_url() classmethod
   - get_info() classmethod
```

### Struktura Pliku - config.py
```
1. Imports
2. Load .env
3. Helper functions (get_radio_stations, etc.)
4. Configuration dicts (RADIO_STATIONS, etc.)
5. Exports (DISCORD_TOKEN, etc.)
```

### Struktura Pliku - user_storage.py (v1.3.0+)
```
1. Imports
2. Logging setup
3. STORAGE_DIR + USERS_FILE constants
4. Storage utilities (ensure_storage_dir, load_users, save_users)
5. User data functions:
   - get_user_data(user_id) - pobierz lub utwórz
   - add_favorite(user_id, track_url, track_title) - dodaj ulubione
   - remove_favorite(user_id, track_url) - usuń ulubione
   - get_favorites(user_id) - pobierz listę
   - add_to_history(user_id, track_url, track_title) - dodaj do historii
   - get_history(user_id, limit=20) - pobierz historię
   - get_user_stats(user_id) - pobierz statystyki
   - increment_skip_count(user_id) - zwiększ skip'i
```

---

## 🔐 Reguły Edycji Kodu

### Edytowanie Istniejących Funkcji
1. ✅ **Zachowaj sygnaturę funkcji** - nie zmieniaj nazwy, parametrów (chyba że deprecation)
2. ✅ **Zachowaj logikę główną** - nie zmienia sposób obsługi danych
3. ✅ **Ulepsz details** - error handling, logging, performance
4. ✅ **Zaktualizuj docstring** - jeśli zmieniła się logika
5. ✅ **Dodaj logging** - każdy błąd powinien być zlogowany

### Dodawanie Nowych Funkcji
1. ✅ **Dodaj docstring** - objaśnij cel i zwracane wartości
2. ✅ **Dodaj type hints** - przynajmniej dla parametrów
3. ✅ **Dodaj logging** - info o starcie, warning o błędach
4. ✅ **Obsłuż wyjątki** - try-except z logowaniem
5. ✅ **Umieść w odpowiednim pliku** - discord commands w main.py, audio w music_handler.py

### Edytowanie Stałych / Konfiguracji
1. ✅ **Zmień wartości domyślne** - OK
2. ✅ **Dodaj nowe opcje** - z komentarzem
3. ❌ **Nie usuwaj starych opcji** - mogą być używane gdzie indziej

---

## 🎵 Specifiki Bot-Musicka

### Strategie YouTube
- **Client priority:** `["web_embedded"]` (single stable client)
- **Fallback:** Jeśli 152-18 (unavailable), szukaj na YouTube
- **Playlist:** `ignoreerrors: True` - pomijaj niedostępne wpisy
- **HTTP 429:** FFmpeg parser + `-cookies config/cookies.txt` (zobacz YOUTUBE_429_FIX.md)

### Spotify Handling
- **Track:** → Szukaj na YouTube (bez DRM)
- **Playlist:** → Dummy entries z wyszukiwaniem
- **Metadane:** ❌ Nie pobieraj (DRM protection)

### Radio API
- **Endpoint:** `https://radyjko.mordorek.dev/api/stations`
- **OpenFM:** `https://stream-cdn-1.open.fm/OFM{openFmId}/ngrp:standard/playlist.m3u8`
- **Timeout:** 10s, fallback do hardcoded stacji

### Error Messages
Dla użytkowników (Discord):
```
❌ Film niedostępny
⚠️ Błąd pobierania
📻 Brak stacji
✅ Dodano: ...
```

Dla logów (bot.log):
```
logger.error("Full error message with context")
logger.warning("Something might be wrong")
logger.info("Action completed successfully")
```

### v1.3.0 Features (Social & Interactive)
- **`/favorites`** - Pokaż ulubione utwory (JSON storage)
- **`/history`** - Historia ostatnio granych (limit 50, wyświetl 20)
- **`/nowplaying`** - Info o aktualnym utworze
- **`/mystats`** - Statystyki użytkownika z embedem (rich embed)
- **`/favorite add|remove`** - Zarządzanie ulubionymi (alpha)
- **Tracking** - Automatyczne dodawanie do historii i skip count
- **Storage** - JSON-based, persistent w `config/user_data/users.json`

---

## 📝 Komunikat Commita

### Format
```
[KATEGORIA] Krótki opis zmiany

Szczegóły (opcjonalnie):
- Co się zmieniło
- Dlaczego
- Jakie problemy rozwiązuje
```

### Kategorie
```
[FIX] - Naprawa błędu
[FEAT] - Nowa funkcja
[REFACTOR] - Poprawa kodu
[DOCS] - Dokumentacja
[PERF] - Optymalizacja
[CHORE] - Aktualizacja zależności
```

### Przykłady
```
[FIX] Dodaj logging do play_next() - pomijanie błędnych wpisów

[FEAT] Dodaj /nowplaying komendę - pokazuje aktualnie grany utwór

[REFACTOR] Wyodrębnij URL detection do osobnych funkcji

[CHORE] Zaktualizuj yt-dlp do najnowszej wersji
```

---

## 🧪 Testowanie

### Przed Committem
1. ✅ Sprawdzić syntax - nie powinno być błędów importu
2. ✅ Sprawdzić logi - niech logger się nie sypie
3. ✅ Sprawdzić logikę - czy się loguje prawidłowo
4. ❌ **Nie testuj na VPS bez zgody!**

### W Docker (lokalne testy)
```bash
docker compose down
docker compose up -d --build
sleep 30
docker compose logs -f
```

### Szukaj w logach
```
❌ ERROR       - Coś się zepsuło
⚠️ WARNING     - Coś dziwnego się dzieje
✅ INFO        - Operacja zakończona
```

---

## 🚀 Wdrażanie

### Production (VPS)
- **Zawsze** pull przed edit
- **Nigdy** nie edytuj direct na VPS
- **Zawsze** test w Docker първо
- **Zawsze** pull request / commit message

### Krytyczne Pliki
❌ **NIGDY nie edituj bez backupu:**
- `main.py` - core bot
- `Dockerfile` - production build
- `.env` - secrets

### Deploy Procedure
```bash
1. Edytuj lokalnie
2. Test w Docker
3. Commit + Push
4. Na VPS: git pull
5. docker compose down
6. docker compose up -d --build
7. docker compose logs -f
```

---

## 📋 Checklist dla Każdej Zmiany

Przed committem **KAŻDY** agent powinien:

- [ ] Kod nie ma syntax errors
- [ ] Logging jest prawidłowy (info, warning, error)
- [ ] Błędy są obsługiwane (try-except)
- [ ] Docstrings są aktualne
- [ ] Nie zmieniłem struktury projektu
- [ ] Nie dodałem zbędnych zależności
- [ ] Komunikat commita ma format [KATEGORIA]
- [ ] Testowałem w Docker
- [ ] README/PLAN/IDEAS są aktualne (jeśli dotyczy)

---

## 🆘 Kiedy Prosić o Pomoc

Agent powinien **prosić użytkownika** gdy:

1. ❓ Nie wiem czy zmiana jest poprawna
2. ❓ Zmiana wymaga refaktora wielu plików
3. ❓ Dodaję nową dużą funkcję
4. ❓ Zmieniam API (sygnatury funkcji)
5. ❓ Nie wiem jakie są intencje użytkownika
6. ❓ Coś się sypie i nie mogę naprawić

**Format:**
```
❓ [PYTANIE] Powinnem zmienić X na Y, aby rozwiązać problem Z?

Kontekst:
- Obecny kod: ...
- Problem: ...
- Propozycja: ...
```

---

## 📖 Dokumentacja Do Aktualizacji

Gdy edytujesz funkcjonalność:

- `README.md` - jeśli zmienia się komenda dla użytkownika
- `PLAN.md` - jeśli dodajesz/kończysz milestone
- `IDEAS.md` - jeśli dodajesz feature idea lub fixujesz issue
- Docstring w kodzie - zawsze
- Komentarze w kodzie - jeśli logika jest skomplikowana

---

## 🎓 Nauka z Historii

### Problemy, które już rozwiązaliśmy
- ✅ YouTube 152-18 → Fallback na wyszukiwanie
- ✅ Spotify DRM → Szukaj na YouTube bez pobierania metadanych
- ✅ FFmpeg crash → Callback handlers + error logging
- ✅ Autocomplete error → Użyj keyword syntax `@app_commands.autocomplete(param=func)`
- ✅ HTTP 429 "Too Many Requests" → FFmpeg YouTube parser + cookies.txt (YOUTUBE_429_FIX.md)

### Czego **NIGDY** nie robić
- ❌ Pobierać metadane Spotify (DRM)
- ❌ Używać cookies na VPS (nie działają)
- ❌ Rzucać błąd zamiast fallback (zawsze mieć plan B)
- ❌ Print zamiast logger (logging daje historię)
- ❌ Testować YouTube bezpośrednio (zawsze fallback)
- ❌ Wyciągać stream URL ręcznie z format array (YouTube blokuje dostęp)

---

## ✨ Best Practices

### Error Handling
```python
try:
    result = await some_async_operation()
except SpecificError as e:
    logger.warning(f"Expected issue: {e}")
    # Fallback or graceful degradation
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### Logging Levels
```python
logger.debug("...")      # Disabled in production
logger.info("✅ ...")    # Normal operations
logger.warning("⚠️ ...") # Something unusual but handled
logger.error("❌ ...")   # Error occurred
```

### Async Functions
```python
@classmethod
async def my_method(cls, param, *, loop=None):
    loop = loop or asyncio.get_event_loop()
    # Use loop.run_in_executor() for blocking operations
    result = await loop.run_in_executor(None, blocking_func, param)
    return result
```

### Discord Interactions
```python
@bot.tree.command(name="mycommand")
async def my_command(interaction: discord.Interaction, param: str):
    await interaction.response.defer()  # Long operations
    # ... do stuff ...
    await interaction.followup.send("Done ✅")
```

---

## 📞 Kontakt i Eskalacja

Jeśli coś nie działa:

1. **Sprawdź logi** - `docker compose logs -f`
2. **Sprawdź PLAN.md** - co jest zaplanowane
3. **Sprawdź IDEAS.md** - co już wiemy o problemach
4. **Zaloguj błąd** - zawsze `logger.error()`
5. **Powiadom użytkownika** - opisy co spróbowaliśmy

---

## 🎯 Podsumowanie

**Każdy agent redagujący ten repo MUSI:**

✅ Znać strukturę projektu  
✅ Następować konwencje kodowania  
✅ Dodawać logging do każdego nowego kodu  
✅ Testować w Docker przed committem  
✅ Aktualizować dokumentację  
✅ Pisać jasne komunikaty commitów  
✅ Prosić pomoc gdy nie wie  

**Ostateczny cel:** Bot, który jest **stabilny, dokumentowany i easy to edytować** dla każdego przyszłego agenta.

---

**Ostatnia aktualizacja:** 27 kwietnia 2026 | **Status:** Aktywny | **Wersja:** v1.3.0 (Social & Interactive)
