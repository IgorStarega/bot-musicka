"""
Bot Musicka v2.0 - Prosty & Zoptymalizowany
"""

import discord
from discord.ext import commands
from discord import app_commands
import config
from music_handler import YTDLSource, get_track_info, is_youtube_url, is_spotify_track
import user_storage
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[logging.FileHandler('bot.log', encoding='utf-8'), logging.StreamHandler()]
)
logger = logging.getLogger('MusicBot')
logging.getLogger('discord').setLevel(logging.WARNING)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.queue = {}
bot.current_track = {}


async def setup_hook():
    await bot.tree.sync()
    logger.info("Komendy zsynchronizowane")
    bot.loop = asyncio.get_event_loop()


bot.setup_hook = setup_hook


async def update_status(text=None, idle=False):
    try:
        if idle:
            await bot.change_presence(activity=discord.Game(name="/play | Radio"))
        elif text:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
    except Exception as e:
        logger.error(f"Status error: {e}")


@bot.event
async def on_ready():
    logger.info(f"Zalogowano jako {bot.user}")
    await update_status(idle=True)


@bot.event
async def on_voice_state_update(member, before, after):
    vc = member.guild.voice_client
    if vc and len(vc.channel.members) == 1:
        logger.info(f"Bot sam, wychodzę...")
        if vc.is_playing():
            vc.stop()
        if member.guild.id in bot.queue:
            bot.queue[member.guild.id] = []
        await vc.disconnect()
        await update_status(idle=True)


async def ensure_voice(interaction):
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            await interaction.user.voice.channel.connect()
        else:
            await interaction.response.send_message("Musisz być na kanale głosowym!")
            return False
    return True


async def play_next(interaction):
    gid = interaction.guild_id
    if gid not in bot.queue or not bot.queue[gid]:
        logger.info("Kolejka pusta")
        bot.current_track.pop(gid, None)
        await update_status(idle=True)
        return
    
    item = bot.queue[gid].pop(0)
    url = item.get("url") if isinstance(item, dict) else item
    title_hint = item.get("title") if isinstance(item, dict) else None
    loop = asyncio.get_event_loop()
    
    try:
        player = await YTDLSource.from_url(url, loop=loop, stream=True)
        if not player:
            logger.warning(f"Nie mogę odtworzyć: {url[:50]}")
            await interaction.channel.send("⏭️ Pomijam...")
            return await play_next(interaction)
        
def after(err):
            if err: logger.error(f"FFmpeg: {err}")
            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(play_next(interaction), loop)
        interaction.guild.voice_client.play(player, after=after)
        bot.current_track[gid] = {"title": player.title, "url": url, "requester": None}
        await update_status(player.title)
        logger.info(f"Odtwarzam: {player.title}")
    except Exception as e:
        logger.error(f"Błąd play_next: {e}")
        bot.current_track.pop(gid, None)
        await update_status(idle=True)


@bot.tree.command(name="play", description="Odtwarza muzykę z YouTube/Spotify")
async def play(interaction: discord.Interaction, search: str):
    if not await ensure_voice(interaction):
        return
    await interaction.response.defer()
    
    url_type = "🔍"
    if is_spotify_track(search):
        url_type = "🎵 Spotify"
    elif is_youtube_url(search):
        url_type = "🎬 YouTube"
    
    logger.info(f"/play: {search[:50]}")
    
    try:
        async def get_track_info(search, loop=asyncio.get_event_loop()):
        entries = info.get("entries", [])
        
        # Filtruj i konwertuj
        urls = []
        titles = []
        for e in entries:
            if e is None or not isinstance(e, dict):
                continue
            if "url" in e:
                urls.append(e["url"])
                titles.append(e.get("title", "Utwór"))
            elif "id" in e:
                urls.append(f"https://www.youtube.com/watch?v={e['id']}")
                titles.append(e.get("title", "Utwór"))
        
        if not urls:
            await interaction.followup.send(f"❌ Nie znaleziono utworów")
            return
        
        # Odtwórz
        if len(urls) == 1:
            if interaction.guild.voice_client.is_playing():
                bot.queue[interaction.guild_id].append({"url": urls[0], "title": titles[0]})
                await interaction.followup.send(f"➕ **{titles[0]}**")
            else:
                loop = asyncio.get_event_loop()
    
    try:
        player = await YTDLSource.from_url(urls[0], loop=loop, stream=True)
                if player:
                    def after(err):
                        if err: logger.error(f"FFmpeg: {err}")
                        asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop)
                    interaction.guild.voice_client.play(player, after=after)
                    bot.current_track[interaction.guild_id] = {"title": player.title, "url": urls[0], "requester": str(interaction.user)}
                    await update_status(player.title)
                    user_storage.add_to_history(interaction.user.id, urls[0], player.title)
                    await interaction.followup.send(f"🎵 **{player.title}**")
                else:
                    await interaction.followup.send("❌ Nie mogę odtworzyć")
        else:
            # Playlista
            if interaction.guild_id not in bot.queue:
                bot.queue[interaction.guild_id] = []
            bot.queue[interaction.guild_id].extend({"url": u, "title": t} for u, t in zip(urls, titles))
            await interaction.followup.send(f"✅ Dodano **{len(urls)}** utworów do kolejki")
            if not interaction.guild.voice_client.is_playing():
                await play_next(interaction)
    
    except Exception as e:
        logger.error(f"/play error: {e}")
        await interaction.followup.send(f"❌ Błąd: {str(e)[:50]}")


@bot.tree.command(name="skip", description="Pomija utwór")
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        user_storage.increment_skip_count(interaction.user.id)
        await interaction.response.send_message("⏭️ Pominięto")
    else:
        await interaction.response.send_message("Nic nie gra")


@bot.tree.command(name="stop", description="Zatrzymuje odtwarzanie")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        bot.queue[interaction.guild_id] = []
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
        await update_status(idle=True)
        await interaction.response.send_message("🛑 Zatrzymano")
    else:
        await interaction.response.send_message("Bot nie gra")


@bot.tree.command(name="radio", description="Odtwarza radio")
async def radio(interaction: discord.Interaction, station: int):
    if not await ensure_voice(interaction):
        return
    await interaction.response.defer()
    
    if station not in config.RADIO_STATIONS:
        await interaction.followup.send("❌ Nieprawidłowa stacja")
        return
    
    st = config.RADIO_STATIONS[station]
    try:
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
        bot.queue[interaction.guild_id] = []
        
        import music_handler
        source = discord.FFmpegPCMAudio(st["url"], **music_handler.FFMPEG_OPTIONS)
        
        def after(err):
            if err: logger.error(f"Radio error: {err}")
            asyncio.run_coroutine_threadsafe(update_status(idle=True), bot.loop)
        
        interaction.guild.voice_client.play(source, after=after)
        await update_status(f"Radio: {st['name']}")
        await interaction.followup.send(f"🎙️ **{st['name']}**")
    except Exception as e:
        logger.error(f"Radio error: {e}")
        await interaction.followup.send(f"❌ Błąd radia")


@bot.tree.command(name="list_radio", description="Lista stacji radiowych")
async def list_radio(interaction: discord.Interaction):
    text = "**Stacje radiowe:**\n"
    for sid, info in config.RADIO_STATIONS.items():
        text += f"`{sid}`: **{info['name']}**\n"
    await interaction.response.send_message(text)


@bot.tree.command(name="queue", description="Pokazuje kolejkę")
async def queue(interaction: discord.Interaction):
    q = bot.queue.get(interaction.guild_id, [])
    if not q:
        return await interaction.response.send_message("Kolejka pusta")
    
    text = "**Kolejka:**\n"
    for i, item in enumerate(q[:10], 1):
        title = item.get("title", item.get("url", "?"))[:50] if isinstance(item, dict) else str(item)[:50]
        text += f"{i}. **{title}**\n"
    
    if len(q) > 10:
        text += f"\n*...i {len(q)-10} więcej*"
    
    await interaction.response.send_message(text)


@bot.tree.command(name="nowplaying", description="Aktualny utwór")
async def nowplaying(interaction: discord.Interaction):
    track = bot.current_track.get(interaction.guild_id)
    if not track:
        return await interaction.response.send_message("Nic nie gra")
    
    await interaction.response.send_message(f"🎵 **{track['title']}**")


@bot.tree.command(name="disconnect", description="Odłącz bota")
async def disconnect(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        bot.queue[interaction.guild_id] = []
        bot.current_track.pop(interaction.guild_id, None)
        if vc.is_playing() or vc.is_paused():
            vc.stop()
        await vc.disconnect()
        await update_status(idle=True)
        await interaction.response.send_message("🔌 Odłączono")
    else:
        await interaction.response.send_message("Bot nie jest połączony")


@bot.tree.command(name="status", description="Status bota")
async def status_cmd(interaction: discord.Interaction):
    ping = round(bot.latency * 1000)
    radio_count = len(config.RADIO_STATIONS)
    await interaction.response.send_message(
        f"✅ **Status:** Ping {ping}ms | {radio_count} stacji radiowych"
    )


# Inicjalizacja
async def main():
    async with bot:
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    if config.DISCORD_TOKEN:
        asyncio.run(main())
    else:
        print("❌ Brak tokenu w .env")