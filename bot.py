# Importazione delle librerie necessarie
import discord
from discord.ext import commands
import yt_dlp
import asyncio

# Configurazione delle intents di Discord
intents = discord.Intents.default()
intents.message_content = True  # Abilita l'accesso al contenuto dei messaggi
intents.voice_states = True  # Abilita l'accesso agli stati vocali

# Opzioni per FFmpeg (usato per lo streaming audio)
FFMPEG_OPTIONS = {
    'options': '-vn',  # Estrae solo l'audio
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'  # Gestisce la riconnessione
}

# Opzioni per youtube-dl (usato per scaricare informazioni sui video)
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': False}

# Definizione della classe MusicBot
class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []  # Coda per le canzoni

    @commands.command()
    async def play(self, ctx, *, search):
        try:
            # Verifica se l'utente è in un canale vocale
            voice_channel = ctx.author.voice.channel if ctx.author.voice else None
            if not voice_channel:
                return await ctx.send("Non sei in un canale vocale")
            
            # Connette il bot al canale vocale se non è già connesso
            if not ctx.voice_client:
                await voice_channel.connect()

            async with ctx.typing():
                # Estrae le informazioni del video da YouTube
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        # È una playlist
                        playlist_title = info.get('title', 'Playlist sconosciuta')
                        await ctx.send(f'Aggiunta playlist: **{playlist_title}**')
                        for entry in info['entries']:
                            url = entry['url']
                            title = entry['title']
                            self.queue.append((url, title))
                            await ctx.send(f'Aggiunto in coda: **{title}**')
                    else:
                        # È un singolo video
                        url = info['url']
                        title = info['title']
                        self.queue.append((url, title))
                        await ctx.send(f'Aggiunto in coda: **{title}**')
                    
                    # Se non c'è nulla in riproduzione, inizia a riprodurre
                    if not ctx.voice_client.is_playing():
                        await self.play_next(ctx)

        except Exception as e:
            await ctx.send(f"Errore: {str(e)}")

    async def play_next(self, ctx):
        if self.queue:
            # Estrae il prossimo brano dalla coda
            url, title = self.queue.pop(0)
            # Riproduce il brano utilizzando FFmpeg
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: self.client.loop.create_task(self.play_next(ctx)))
            await ctx.send(f"Ora in riproduzione: {title}")
        else:
            # Se la coda è vuota, disconnette il bot dal canale vocale
            await ctx.voice_client.disconnect()

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            # Ferma la riproduzione corrente
            ctx.voice_client.stop()
            await ctx.send("Brano saltato.")
        else:
            await ctx.send("Non c'è nulla in riproduzione.")

# Configurazione del bot
client = commands.Bot(command_prefix='!', intents=intents)
client.add_cog(MusicBot(client))

# Avvio del bot
client.run('YOUR_BOT_TOKEN')