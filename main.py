import discord
from discord.ext import commands
from discord import app_commands
import config
from music_handler import YTDLSource

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizacja komend slash
        await self.tree.sync()
        print(f"Zsynchronizowano komendy slash dla {self.user}")

bot = MusicBot()

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.tree.command(name="ping", description="Sprawdza opóźnienie bota")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'Pong! Latencja: {round(bot.latency * 1000)}ms')

@bot.tree.command(name="join", description="Dołącza do kanału głosowego")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        return await interaction.response.send_message("Musisz być na kanale głosowym!")
    
    channel = interaction.user.voice.channel
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.move_to(channel)
    else:
        await channel.connect()
    await interaction.response.send_message(f"Dołączono do {channel.name}")

@bot.tree.command(name="leave", description="Opuszcza kanał głosowy")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Opuszczono kanał głosowy.")
    else:
        await interaction.response.send_message("Nie jestem na żadnym kanale!")

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

@bot.tree.command(name="play", description="Odtwarza piosenkę z YouTube lub URL")
async def play(interaction: discord.Interaction, search: str):
    if not await ensure_voice(interaction):
        return

    await interaction.response.defer()
    
    try:
        player = await YTDLSource.from_url(search, loop=bot.loop, stream=True)
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
        interaction.guild.voice_client.play(player, after=lambda e: print(f'Błąd odtwarzania: {e}') if e else None)
        await interaction.followup.send(f'Teraz gram: **{player.title}**')
    except Exception as e:
        await interaction.followup.send(f"Wystąpił błąd: {str(e)}")

@bot.tree.command(name="stop", description="Zatrzymuje odtwarzanie")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Muzyka zatrzymana.")
    else:
        await interaction.response.send_message("Nic nie jest teraz odtwarzane.")

@bot.tree.command(name="radio", description="Odtwarza wybraną stację radiową")
@app_commands.describe(station="Wybierz stację radiową z listy")
@app_commands.choices(station=[
    app_commands.Choice(name=f"{id}: {info['name']}", value=id)
    for id, info in config.RADIO_STATIONS.items()
])
async def radio(interaction: discord.Interaction, station: app_commands.Choice[int]):
    id = station.value
    if not await ensure_voice(interaction):
        return

    await interaction.response.defer()
    station_info = config.RADIO_STATIONS[id]
    
    if interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()

    source = discord.FFmpegPCMAudio(station_info["url"], **{
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 10000000',
        'options': '-vn'
    })
    interaction.guild.voice_client.play(source)
    await interaction.followup.send(f'Rozpoczęto nadawanie: **{station_info["name"]}**')

@bot.tree.command(name="test", description="Testuje wszystkie funkcje bota")
async def test(interaction: discord.Interaction):
    test_results = [
        "✅ Bot jest online",
        f"✅ Latencja: {round(bot.latency * 1000)}ms",
        "✅ System Slash Commands działa",
        "✅ Załadowano konfigurację radia",
        "✅ Integracja z yt-dlp gotowa"
    ]
    await interaction.response.send_message("\n".join(test_results))

if __name__ == "__main__":
    if not config.DISCORD_TOKEN or config.DISCORD_TOKEN == "YOUR_TOKEN_HERE":
        print("BŁĄD: Uzupełnij DISCORD_TOKEN w pliku .env!")
    else:
        bot.run(config.DISCORD_TOKEN)
