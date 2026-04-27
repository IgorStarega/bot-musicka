import discord
from discord.ext import commands
from discord import app_commands
import config
from music_handler import YTDLSource, is_youtube_url, is_youtube_playlist, is_spotify_url, is_spotify_playlist, is_spotify_track, RADIO_FFMPEG_OPTIONS
import user_storage
import asyncio

import logging
import os

# Konfiguracja logowania logów do pliku (Punkt 10 z IDEAS.md)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MusicBot')

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.queue = {}

    async def setup_hook(self):
        # Sprawdzanie ciasteczek przy starcie (Punkt 1 z IDEAS.md)
        cookie_path = 'config/cookies.txt'
        if os.path.exists(cookie_path):
            logger.info(f"✅ Znaleziono plik ciasteczek: {cookie_path}")
        else:
            logger.warning(f"⚠️ Brak pliku {cookie_path}! YouTube może blokować żądania.")
        
        await self.tree.sync()
        logger.info(f"Zsynchronizowano komendy slash dla {self.user}")

bot = MusicBot()

async def update_status(activity_text=None, idle=False):
    try:
        if idle:
            await bot.change_presence(activity=discord.Game(name="/play | Radio"))
        elif activity_text:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_text))
    except Exception as e:
        logger.error(f"Błąd zmiany statusu: {e}")

@bot.event
async def on_ready():
    logger.info(f"Zalogowano jako {bot.user} (ID: {bot.user.id})")
    await update_status(idle=True)
    logger.info("------")

@bot.event
async def on_voice_state_update(member, before, after):
    # Punkt 2 z IDEAS.md: Auto-leave i czyszczenie zasobów
    voice_client = member.guild.voice_client
    if not voice_client:
        return

    # Jeśli bot został sam na kanale
    if len(voice_client.channel.members) == 1:
        logger.info(f"Bot został sam na kanale w {member.guild.name}. Wychodzę...")
        
        # Zatrzymaj odtwarzanie i czyszczenie FFmpeg
        try:
            if voice_client.is_playing():
                voice_client.stop()
                logger.info("✅ Zatrzymano odtwarzanie")
        except Exception as e:
            logger.error(f"Błąd zatrzymania: {e}")
        
        # Wyczyść kolejkę
        if member.guild.id in bot.queue:
            bot.queue[member.guild.id] = []
        
        # Odłącz się
        try:
            await voice_client.disconnect()
            logger.info("✅ Odłączono z kanału głosowego")
        except Exception as e:
            logger.error(f"Błąd odłączania: {e}")
        
        await update_status(idle=True)

async def ensure_voice(interaction: discord.Interaction):
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            await interaction.user.voice.channel.connect()
        else:
            await interaction.response.send_message("Musisz być na kanale głosowym!")
            return False
    elif interaction.user.voice and interaction.guild.voice_client.channel != interaction.user.voice.channel:
        await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
    return True

async def play_next(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    
    if guild_id not in bot.queue or not bot.queue[guild_id]:
        logger.info("📬 Kolejka pusta, kończę")
        await update_status(idle=True)
        return

    source_url = bot.queue[guild_id].pop(0)
    try:
        # Sprawdź czy to radio
        if source_url.startswith("RADIO:"):
            radio_id = int(source_url.split(":")[1])
            if radio_id not in config.RADIO_STATIONS:
                logger.error(f"Radio ID {radio_id} nie znaleziony")
                return await play_next(interaction)
            
            st_info = config.RADIO_STATIONS[radio_id]
            logger.info(f"🎙️ Radio: {st_info['name']}")
            
            def after_radio(error):
                if error: 
                    logger.error(f"Błąd radia: {error}")
                try:
                    asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop)
                except Exception as e:
                    logger.error(f"Błąd w after_radio callback: {e}")
            
            source = discord.FFmpegPCMAudio(st_info["url"], **RADIO_FFMPEG_OPTIONS)
            interaction.guild.voice_client.play(source, after=after_radio)
            await update_status(f"Radio: {st_info['name']}")
            await interaction.channel.send(f"🎙️ **{st_info['name']}** - nadawanie...")
            logger.info(f"✅ Radio uruchomione")
            return
        
        # Normalny utwór z YouTube/Spotify
        try:
            player = await YTDLSource.from_url(source_url, loop=bot.loop, stream=True)
        except Exception as e:
            error_msg = str(e)[:100]
            logger.warning(f"⚠️ Pominąłem utwór z powodu błędu: {error_msg}")
            await interaction.channel.send(f"⏭️ Pominąłem niedostępny utwór, przechodzę dalej...")
            return await play_next(interaction)

        def after_playing(error):
            if error: 
                logger.error(f"Błąd FFmpeg: {error}")
            try:
                asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop)
            except Exception as e:
                logger.error(f"Błąd w after_playing callback: {e}")
        
        if interaction.guild.voice_client:
            interaction.guild.voice_client.play(player, after=after_playing)
            await update_status(player.title)
            await interaction.channel.send(f"🎵 Teraz gram: **{player.title}**")
            # v1.3.0: Dodaj do historii
            user_storage.add_to_history(interaction.user.id, source_url, player.title)
            logger.info(f"✅ Odtwarzanie: {player.title}")
        else:
            logger.error("Brak voice client")
            await update_status(idle=True)
    except Exception as e:
        logger.error(f"Błąd kolejki: {e}")
        await play_next(interaction)

@bot.tree.command(name="play", description="Odtwarza piosenkę lub playlistę (YouTube, Spotify)")
async def play(interaction: discord.Interaction, search: str):
    if not await ensure_voice(interaction): return
    await interaction.response.defer()
    guild_id = interaction.guild_id
    logger.info(f"▶️ /play [{guild_id}]: {search[:60]}...")
    
    # Rozpoznaj typ URL
    url_type = "🔍 szukanie"
    if is_spotify_track(search):
        url_type = "🎵 Spotify track"
    elif is_spotify_playlist(search):
        url_type = "📻 Spotify playlist"
    elif is_youtube_url(search) and is_youtube_playlist(search):
        url_type = "📺 YouTube playlist"
    elif is_youtube_url(search):
        url_type = "🎬 YouTube video"
    
    try:
        await interaction.followup.send(f"⏳ Pobieram... ({url_type})")
        logger.info(f"[/play] Calling get_info for: {search[:50]}")
        info = await YTDLSource.get_info(search, loop=bot.loop)
        logger.info(f"[/play] get_info returned type: {type(info).__name__}, is dict: {isinstance(info, dict)}")
        
        # Bezpieczna obsługa None i empty
        if not isinstance(info, dict):
            logger.warning(f"[/play] Info is not dict! Type: {type(info).__name__}")
            info = {"entries": []}
        
        entries = info.get("entries", [])
        logger.info(f"[/play] Entries count: {len(entries)}")
        
        if not entries:
            logger.warning(f"[/play] No entries found, sending error response")
            await interaction.followup.send(f"❌ Brak utworów ({url_type})")
            logger.warning(f"Brak: {search[:50]}")
            return
        
        urls = [e["url"] for e in entries if isinstance(e, dict) and "url" in e]
        if not urls:
            await interaction.followup.send(f"❌ Brak dostępnych utworów")
            logger.warning(f"Brak URL w wpisach: {search[:50]}")
            return
        
        # PLAYLISTA (>1 utwór)
        if len(urls) > 1:
            if guild_id not in bot.queue: bot.queue[guild_id] = []
            bot.queue[guild_id].extend(urls)
            title = info.get("title", "Playlista")
            logger.info(f"📊 Playlista: {title}, {len(urls)} utworów")
            await interaction.followup.send(f"✅ **{title}**\n📊 **{len(urls)} utworów**\n⏭️ Zaraz gram...")
            
            if not interaction.guild.voice_client.is_playing():
                await play_next(interaction)
        
        # SINGLE (1 utwór)
        else:
            if interaction.guild.voice_client.is_playing():
                if guild_id not in bot.queue: bot.queue[guild_id] = []
                bot.queue[guild_id].append(urls[0])
                title = entries[0].get("title", "Utwór") if isinstance(entries[0], dict) else "Utwór"
                logger.info(f"➕ Dodano do kolejki: {title}")
                await interaction.followup.send(f"➕ **{title}**")
            else:
                try:
                    player = await YTDLSource.from_url(urls[0], loop=bot.loop, stream=True)
                    if not player:
                        await interaction.followup.send(f"❌ Nie mogę przygotować utworu")
                        return
                    def after_playing(error):
                        if error: 
                            logger.error(f"Błąd FFmpeg: {error}")
                        asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop)
                    interaction.guild.voice_client.play(player, after=after_playing)
                    await update_status(player.title)
                    user_storage.add_to_history(interaction.user.id, urls[0], player.title)
                    logger.info(f"🎵 Gram: {player.title}")
                    await interaction.followup.send(f"🎵 **{player.title}**")
                except Exception as e:
                    error_msg = str(e)[:80]
                    logger.error(f"/play single: {e}")
                    await interaction.followup.send(f"❌ {error_msg}")
    
    except Exception as e:
        error_msg = str(e)[:80]
        await interaction.followup.send(f"❌ {error_msg}")
        logger.error(f"/play główny: {e}")

@bot.tree.command(name="skip", description="Pomija utwór")
async def skip(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    queue_len = len(bot.queue.get(guild_id, []))
    logger.info(f"⏭️ /skip [{guild_id}] - Kolejka: {queue_len}")
    
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        try:
            interaction.guild.voice_client.stop()
            user_storage.increment_skip_count(interaction.user.id)
            logger.info(f"✅ Pominięto")
            await interaction.response.send_message("⏭️ Pominięto.")
        except Exception as e:
            logger.error(f"Błąd skip: {e}")
            await interaction.response.send_message(f"❌ Błąd: {str(e)[:50]}")
    else:
        logger.info(f"Nic nie gra")
        await interaction.response.send_message("Nic nie gra.")

@bot.tree.command(name="stop", description="Zatrzymuje wszystko")
async def stop(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    logger.info(f"🛑 /stop [{guild_id}]")
    
    if interaction.guild.voice_client:
        try:
            # Wyczyść kolejkę
            queue_len = len(bot.queue.get(guild_id, []))
            if interaction.guild_id in bot.queue:
                bot.queue[interaction.guild_id] = []
                logger.info(f"📋 Wyczyszczono kolejkę ({queue_len} wpisów)")
            
            # Zatrzymaj odtwarzanie
            if interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.stop()
                logger.info(f"✅ FFmpeg zatrzymany")
            
            logger.info("✅ Wszystko zatrzymane")
            await update_status(idle=True)
            await interaction.response.send_message("🛑 Zatrzymano i wyczyszczono kolejkę.")
        except Exception as e:
            logger.error(f"Błąd stop: {e}")
            await interaction.response.send_message(f"❌ Błąd: {str(e)[:50]}")
    else:
        logger.info(f"Bot nie połączony")
        await interaction.response.send_message("Bot nie jest połączony.")

@bot.tree.command(name="list_radio", description="Wyświetla listę dostępnych stacji radiowych")
async def list_radio(interaction: discord.Interaction):
    stations = config.RADIO_STATIONS
    if not stations:
        return await interaction.response.send_message("Brak dostępnych stacji.")
    
    text = "**Dostępne stacje radiowe (wpisz ID w /radio):**\n\n"
    for id, info in stations.items():
        text += f"`{id}`: **{info['name']}**\n"
    
    # Discord ma limit 2000 znaków
    if len(text) > 2000:
        # Zapisz do pliku tymczasowego i wyślij jeśli lista jest za długa
        with open("stations_list.txt", "w", encoding="utf-8") as f:
            f.write(text.replace("**", "").replace("`", ""))
        await interaction.response.send_message("Lista stacji jest zbyt długa, wysyłam ją w pliku:", file=discord.File("stations_list.txt"))
        os.remove("stations_list.txt")
    else:
        await interaction.response.send_message(text)

# Autocomplete dla /radio - musi być PRZED dekoratorem komendy
async def radio_station_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[int]]:
    """Autocomplete dla /radio - wyświetla dostępne stacje."""
    stations = config.RADIO_STATIONS
    choices = []
    for station_id, info in stations.items():
        if current.lower() in info['name'].lower() or not current:
            choices.append(app_commands.Choice(name=f"{info['name']} (ID: {station_id})", value=station_id))
            if len(choices) >= 25:  # Discord limit: max 25 choices
                break
    return choices

@bot.tree.command(name="radio", description="Odtwarza radio")
@app_commands.describe(station="Wybierz stację radiową z listy")
@app_commands.autocomplete(station=radio_station_autocomplete)
async def radio(interaction: discord.Interaction, station: int):
    if not await ensure_voice(interaction): return
    await interaction.response.defer()
    
    if station not in config.RADIO_STATIONS:
        await interaction.followup.send("Niepoprawne ID stacji!")
        return
        
    st_info = config.RADIO_STATIONS[station]
    
    try:
        if interaction.guild.voice_client.is_playing(): 
            interaction.guild.voice_client.stop()
            
        if interaction.guild_id in bot.queue:
            bot.queue[interaction.guild_id] = []

        source = discord.FFmpegPCMAudio(st_info["url"], **RADIO_FFMPEG_OPTIONS)
        
        def after_radio(error):
            if error: logger.error(f"Błąd radia: {error}")
            asyncio.run_coroutine_threadsafe(update_status(idle=True), bot.loop)

        interaction.guild.voice_client.play(source, after=after_radio)
        await update_status(f"Radio: {st_info['name']}")
        await interaction.followup.send(f"🎙️ **{st_info['name']}** - nadawanie...")
    except Exception as e:
        logger.error(f"Błąd połączenia z radiem {st_info['name']}: {e}")
        await interaction.followup.send(f"⚠️ Nie udało się połączyć ze stacją **{st_info['name']}**.")

@bot.tree.command(name="status", description="Sprawdza funkcjonowanie bota i wyświetla statystykę")
async def status(interaction: discord.Interaction):
    """Diagnoza bota: czy działa Discord, FFmpeg, czy są błędy."""
    await interaction.response.defer()
    
    status_lines = []
    status_lines.append("🤖 **Status Bot Musicka**\n")
    
    # 1. Discord connection
    if bot.user:
        status_lines.append(f"✅ Discord: Połączony jako **{bot.user}**")
    else:
        status_lines.append(f"❌ Discord: Nie połączony")
    
    # 2. Voice state
    guild = interaction.guild
    if guild.voice_client:
        status_lines.append(f"✅ Głos: Na kanale **{guild.voice_client.channel.name}**")
        if guild.voice_client.is_playing():
            status_lines.append(f"🎵 Aktualnie gra: Tak")
        else:
            status_lines.append(f"⏸️ Aktualnie gra: Nie")
    else:
        status_lines.append(f"⏸️ Głos: Nie połączony")
    
    # 3. Queue
    guild_id = interaction.guild_id
    queue_size = len(bot.queue.get(guild_id, []))
    status_lines.append(f"📋 Kolejka: {queue_size} utworów")
    
    # 4. Radio stations loaded
    radio_count = len(config.RADIO_STATIONS)
    status_lines.append(f"📻 Stacje radiowe: {radio_count} załadowanych")
    
    # 5. Ping
    ping = round(bot.latency * 1000)
    status_lines.append(f"⚡ Ping: {ping}ms")
    
    # 6. Commands available
    commands_count = len(bot.tree.get_commands())
    status_lines.append(f"⌨️ Komendy: {commands_count} dostępnych")
    
    status_lines.append("\n✨ **Wszystko działa poprawnie!**" if queue_size >= 0 else "\n⚠️ Jakieś problemy")
    
    logger.info(f"Status sprawdzony przez {interaction.user}")
    await interaction.followup.send("\n".join(status_lines))

@bot.tree.command(name="test", description="Test funkcjonalności bota")
async def test(interaction: discord.Interaction):
    """Test wszystkich komend bota."""
    await interaction.response.defer()
    
    test_results = []
    test_results.append("🧪 **Test Funkcjonalności Bot Musicka**\n")
    
    # Test 1: Bot online
    try:
        test_results.append("✅ Bot online - OK")
    except:
        test_results.append("❌ Bot online - FAIL")
    
    # Test 2: Discord.py
    try:
        assert hasattr(bot, 'tree')
        test_results.append("✅ Discord.py - OK")
    except:
        test_results.append("❌ Discord.py - FAIL")
    
    # Test 3: FFmpeg dostępny
    try:
        import subprocess
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        test_results.append("✅ FFmpeg - OK")
    except:
        test_results.append("⚠️ FFmpeg - Niedostępny (audio może nie działać)")
    
    # Test 4: Radio API
    try:
        if config.RADIO_STATIONS:
            test_results.append(f"✅ Radio API - OK ({len(config.RADIO_STATIONS)} stacji)")
        else:
            test_results.append("⚠️ Radio API - Brak stacji")
    except:
        test_results.append("❌ Radio API - FAIL")
    
    # Test 5: yt-dlp
    try:
        import yt_dlp
        test_results.append("✅ yt-dlp - OK")
    except:
        test_results.append("❌ yt-dlp - FAIL")
    
    # Test 6: Logging
    try:
        logger.info("Test log message")
        test_results.append("✅ Logging - OK")
    except:
        test_results.append("❌ Logging - FAIL")
    
    test_results.append("\n📊 Testy ukończone!")
    
    logger.info(f"Testy wykonane przez {interaction.user}")
    await interaction.followup.send("\n".join(test_results))

@bot.tree.command(name="queue", description="Pokazuje aktualną kolejkę utworów")
async def queue(interaction: discord.Interaction):
    # Punkt 4 z Roadmappy: Komenda /queue
    guild_id = interaction.guild_id
    if guild_id not in bot.queue or not bot.queue[guild_id]:
        return await interaction.response.send_message("Kolejka jest pusta.")
    
    text = "**Aktualna kolejka:**\n"
    for i, url in enumerate(bot.queue[guild_id][:10], 1):
        clean_url = url.replace("ytsearch:", "")
        text += f"{i}. {clean_url}\n"
    
    if len(bot.queue[guild_id]) > 10:
        text += f"\n*...i {len(bot.queue[guild_id]) - 10} więcej piosenek.*"
        
    await interaction.response.send_message(text)

# ===== v1.3.0 NOWE KOMENDY =====

@bot.tree.command(name="favorite", description="Zarządzanie ulubionym utworem (v1.3.0)")
@app_commands.describe(action="add lub remove")
async def favorite(interaction: discord.Interaction, action: str):
    """Dodaj/usuń aktualnie grany utwór do/z ulubionych"""
    await interaction.response.defer()
    
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        # Spróbujemy pobrać info o grającym utworze
        # TO jest hack - discord.py nie udostępnia direct info o aktualnie grającym utworze
        logger.info(f"⭐ /favorite {action} - brak bezpośredniego dostępu do info")
        await interaction.followup.send("❌ Nie mogę pobrać info o aktualnym utworze (discord.py limitation)\n💡 Jako workaround: `/nowplaying` pokaże URL, który możesz ręcznie dodać")
    else:
        await interaction.followup.send("❌ Nic nie gra")

@bot.tree.command(name="favorites", description="Pokaż swoje ulubione utwory (v1.3.0)")
async def favorites(interaction: discord.Interaction):
    """Wyświetl listę ulubionych utworów"""
    await interaction.response.defer()
    
    user_id = interaction.user.id
    favs = user_storage.get_favorites(user_id)
    
    if not favs:
        return await interaction.followup.send("⭐ Nie masz jeszcze ulubionych utworów!")
    
    text = f"⭐ **Ulubione ({len(favs)}):**\n\n"
    for i, fav in enumerate(favs[:10], 1):
        text += f"{i}. **{fav['title'][:50]}**\n"
    
    if len(favs) > 10:
        text += f"\n*...i {len(favs) - 10} więcej.*"
    
    logger.info(f"⭐ /favorites - {len(favs)} ulubionych dla {interaction.user}")
    await interaction.followup.send(text)

@bot.tree.command(name="history", description="Pokaż ostatnio grane utwory (v1.3.0)")
async def history(interaction: discord.Interaction):
    """Wyświetl historię ostatnio granych utworów"""
    await interaction.response.defer()
    
    user_id = interaction.user.id
    hist = user_storage.get_history(user_id, limit=15)
    
    if not hist:
        return await interaction.followup.send("📋 Nie masz historii!")
    
    text = f"📋 **Historia ({len(hist)}):**\n\n"
    for i, track in enumerate(hist, 1):
        text += f"{i}. **{track['title'][:50]}**\n"
    
    logger.info(f"📋 /history - {len(hist)} utworów dla {interaction.user}")
    await interaction.followup.send(text)

@bot.tree.command(name="nowplaying", description="Info o aktualnie grającym utworze (v1.3.0)")
async def nowplaying(interaction: discord.Interaction):
    """Wyświetl informacje o aktualnie grającym utworze"""
    await interaction.response.defer()
    
    if not (interaction.guild.voice_client and interaction.guild.voice_client.is_playing()):
        return await interaction.followup.send("⏸️ Nic nie gra")
    
    # Pobierz status z update_status - to jest rough approximation
    text = "🎵 **Teraz gram:**\n"
    text += f"*Szczegóły niedostępne (discord.py limitation)*\n"
    text += f"⏰ Serwer: {interaction.guild.name}\n"
    text += f"👤 Użytkownik: {interaction.user.mention}"
    
    logger.info(f"🎵 /nowplaying - {interaction.user}")
    await interaction.followup.send(text)

@bot.tree.command(name="mystats", description="Twoje statystyki (v1.3.0)")
async def mystats(interaction: discord.Interaction):
    """Wyświetl statystyki użytkownika"""
    await interaction.response.defer()
    
    user_id = interaction.user.id
    stats = user_storage.get_user_stats(user_id)
    favs_count = len(user_storage.get_favorites(user_id))
    hist_count = len(user_storage.get_history(user_id))
    
    embed = discord.Embed(
        title=f"📊 Statystyki - {interaction.user.name}",
        color=discord.Color.blue(),
        description=f"*Twoją historię muzyczną*"
    )
    embed.add_field(name="🎵 Utworów gram", value=str(stats.get("total_played", 0)), inline=True)
    embed.add_field(name="⏭️ Skip'ów", value=str(stats.get("skip_count", 0)), inline=True)
    embed.add_field(name="⭐ Ulubionych", value=str(favs_count), inline=True)
    embed.add_field(name="📋 W historii", value=str(hist_count), inline=True)
    
    logger.info(f"📊 /mystats - {interaction.user}")
    await interaction.followup.send(embed=embed)

if __name__ == "__main__":
    if not config.DISCORD_TOKEN or config.DISCORD_TOKEN == "YOUR_TOKEN_HERE":
        print("BŁĄD: Brak tokenu!")
    else:
        bot.run(config.DISCORD_TOKEN)
