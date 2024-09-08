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
                return await ctx.send("Non sei un un canale vocale")
            
            # Connette il bot al canale vocale se non è già connesso
            if not ctx.voice_client:
                await voice_channel.connect()

            async with ctx.typing():
                # Estrae le informazioni del video da YouTube
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    url = info['url']
                    title = info['title']
                    
                    # Aggiunge la canzone alla coda
                    self.queue.append((url, title))
                    await ctx.send(f'Aggiunto in coda: **{title}**')

                # Se non sta già riproducendo, inizia la riproduzione
                if not ctx.voice_client.is_playing():
                    await self.play_next(ctx)  

        except Exception as e:
            print(f"Errore nella riproduzione del brano: {e}")

    async def play_next(self, ctx):
        try:
            if self.queue:
                # Prende la prossima canzone dalla coda
                url, title = self.queue.pop(0)
                # Crea una sorgente audio
                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                # Riproduce la canzone
                ctx.voice_client.play(source, after=lambda _: self.client.loop.create_task(self.play_next(ctx)))
                await ctx.send(f'In riproduzione: **{title}**')
            elif not ctx.voice_client.is_playing():
                await ctx.send("La coda è vuota!") 
        except Exception as e:
            print(f"Errore nella riproduzione del brano: {e}")

    @commands.command()
    async def skip(self, ctx):
        # Salta la canzone corrente
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skippato")

    @commands.command()
    async def pause(self, ctx):
        # Mette in pausa la riproduzione
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Brano in pausa")
        else:
            await ctx.send("Nessun brano in riproduzione")

    @commands.command()
    async def resume(self, ctx):
        # Riprende la riproduzione
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Ripreso")

# Creazione dell'istanza del bot
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    # Evento chiamato quando il bot è pronto e connesso
    print(f"Connected as {client.user}")
    print(f"Connected to the following guilds:")
    for guild in client.guilds:
        print(f" - {guild.name}")
    print(f"Prefix: {client.command_prefix}")

async def main():
    try:
        # Aggiunge il cog MusicBot al bot
        await client.add_cog(MusicBot(client))
        # Avvia il bot
        f = open("token.txt", "r")
        await client.start(f.read())
        f.close()  # Chiude il file con il token
    except Exception as e:
        print(f"Error starting bot: {e}")

# Esegue la funzione main in modo asincrono
asyncio.run(main())