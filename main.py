import discord
from discord.ext import commands
from discord import app_commands
import config
from music_handler import YTDLSource
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
        if member.guild.id in bot.queue:
            bot.queue[member.guild.id] = []
        await voice_client.disconnect()
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
        await update_status(idle=True)
        return

    source_url = bot.queue[guild_id].pop(0)
    try:
        # Próba uzyskania info z obsługą błędów
        try:
            player = await YTDLSource.from_url(source_url, loop=bot.loop, stream=True)
        except Exception as e:
            await interaction.channel.send(f"⚠️ Pominąłem utwór z powodu błędu: `{str(e)[:100]}`")
            return await play_next(interaction)

        def after_playing(error):
            if error: print(f"Błąd FFmpeg: {error}")
            asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop)
        
        if interaction.guild.voice_client:
            interaction.guild.voice_client.play(player, after=after_playing)
            await update_status(player.title)
            await interaction.channel.send(f"Teraz gram: **{player.title}**")
        else:
            await update_status(idle=True)
    except Exception as e:
        print(f"Błąd kolejki: {e}")
        await play_next(interaction)

@bot.tree.command(name="play", description="Odtwarza piosenkę lub playlistę")
async def play(interaction: discord.Interaction, search: str):
    if not await ensure_voice(interaction): return
    await interaction.response.defer()
    guild_id = interaction.guild_id
    try:
        info = await YTDLSource.get_info(search, loop=bot.loop)
        if info and "entries" in info and info["entries"] is not None:
            urls = [e["url"] for e in info["entries"] if e and "url" in e]
            if not urls:
                await interaction.followup.send("Nie znaleziono utworów w tym linku.")
                return
            if guild_id not in bot.queue: bot.queue[guild_id] = []
            bot.queue[guild_id].extend(urls)
            title = info.get("title", "Nieznana playlista")
            await interaction.followup.send(f"Dodano playlistę: **{title}** ({len(urls)} utworów)")
            if not interaction.guild.voice_client.is_playing(): await play_next(interaction)
        elif info:
            if interaction.guild.voice_client.is_playing():
                if guild_id not in bot.queue: bot.queue[guild_id] = []
                bot.queue[guild_id].append(info["url"])
                title = info.get("title", "Nieznany utwór")
                await interaction.followup.send(f"Dodano do kolejki: **{title}**")
            else:
                player = await YTDLSource.from_url(search, loop=bot.loop, stream=True)
                def after_playing(error):
                    if error: print(f"Błąd: {error}")
                    asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop)
                interaction.guild.voice_client.play(player, after=after_playing)
                await update_status(player.title)
                await interaction.followup.send(f"Teraz gram: **{player.title}**")
    except Exception as e:
        await interaction.followup.send(f"Błąd: {str(e)}")

@bot.tree.command(name="skip", description="Pomija utwór")
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Pominięto.")
    else: await interaction.response.send_message("Nic nie gra.")

@bot.tree.command(name="stop", description="Zatrzymuje wszystko")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        if interaction.guild_id in bot.queue: bot.queue[interaction.guild_id] = []
        interaction.guild.voice_client.stop()
        await update_status(idle=True)
        await interaction.response.send_message("Zatrzymano i wyczyszczono kolejkę.")

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

@bot.tree.command(name="radio", description="Odtwarza radio")
@app_commands.describe(station="Wybierz stację")
async def radio(interaction: discord.Interaction, station: int):
    if not await ensure_voice(interaction): return
    await interaction.response.defer()
    
    if station not in config.RADIO_STATIONS:
        await interaction.followup.send("Niepoprawne ID stacji!")
        return
        
    st_info = config.RADIO_STATIONS[station]
    
    # Punkt 4 z IDEAS.md: Sprawdzanie dostępności streamu radiowego
    try:
        if interaction.guild.voice_client.is_playing(): 
            interaction.guild.voice_client.stop()
            
        # Punkt 2 z IDEAS.md: Czyszczenie kolejki przy włączeniu radia
        if interaction.guild_id in bot.queue:
            bot.queue[interaction.guild_id] = []

        source = discord.FFmpegPCMAudio(st_info["url"], **{"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 10000000", "options": "-vn"})
        
        def after_radio(error):
            if error: logger.error(f"Błąd radia: {error}")
            asyncio.run_coroutine_threadsafe(update_status(idle=True), bot.loop)

        interaction.guild.voice_client.play(source, after=after_radio)
        await update_status(f"Radio: {st_info['name']}")
        await interaction.followup.send(f"Nadawanie radia: **{st_info['name']}**")
    except Exception as e:
        logger.error(f"Błąd połączenia z radiem {st_info['name']}: {e}")
        await interaction.followup.send(f"⚠️ Nie udało się połączyć ze stacją **{st_info['name']}**.")

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

if __name__ == "__main__":
    if not config.DISCORD_TOKEN or config.DISCORD_TOKEN == "YOUR_TOKEN_HERE":
        print("BŁĄD: Brak tokenu!")
    else:
        bot.run(config.DISCORD_TOKEN)
