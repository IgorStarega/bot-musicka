import discord
from discord.ext import commands
from discord import app_commands
import config
from music_handler import YTDLSource
import asyncio

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.queue = {}

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Zsynchronizowano komendy slash dla {self.user}")

bot = MusicBot()

async def update_status(activity_text=None, idle=False):
    try:
        if idle:
            await bot.change_presence(activity=discord.Game(name="/play | Radio"))
        elif activity_text:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_text))
    except Exception as e:
        print(f"Błąd zmiany statusu: {e}")

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user} (ID: {bot.user.id})")
    await update_status(idle=True)
    print("------")

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
        player = await YTDLSource.from_url(source_url, loop=bot.loop, stream=True)
        def after_playing(error):
            if error: print(f"Błąd: {error}")
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
        if "entries" in info:
            urls = [e["url"] for e in info["entries"] if e]
            if guild_id not in bot.queue: bot.queue[guild_id] = []
            bot.queue[guild_id].extend(urls)
            title = info.get("title", "Nieznana playlista")
            await interaction.followup.send(f"Dodano playlistę: **{title}** ({len(urls)} utworów)")
            if not interaction.guild.voice_client.is_playing(): await play_next(interaction)
        else:
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

@bot.tree.command(name="radio", description="Odtwarza radio")
@app_commands.describe(station="Wybierz stację")
@app_commands.choices(station=[app_commands.Choice(name=f"{id}: {info['name']}", value=id) for id, info in config.RADIO_STATIONS.items()])
async def radio(interaction: discord.Interaction, station: app_commands.Choice[int]):
    if not await ensure_voice(interaction): return
    await interaction.response.defer()
    st_id = station.value
    st_info = config.RADIO_STATIONS[st_id]
    if interaction.guild.voice_client.is_playing(): interaction.guild.voice_client.stop()
    source = discord.FFmpegPCMAudio(st_info["url"], **{"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 10000000", "options": "-vn"})
    interaction.guild.voice_client.play(source)
    await update_status(f"Radio: {st_info['name']}")
    await interaction.followup.send(f"Radio: **{st_info['name']}**")

if __name__ == "__main__":
    if not config.DISCORD_TOKEN or config.DISCORD_TOKEN == "YOUR_TOKEN_HERE":
        print("BŁĄD: Brak tokenu!")
    else:
        bot.run(config.DISCORD_TOKEN)
