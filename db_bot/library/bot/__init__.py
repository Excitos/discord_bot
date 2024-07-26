from discord import Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase

PREFIX = "+"
OWNER_ID = [1252917419689902080]

class Bot(BotBase):
    def __init__(self):

        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        super().__init__(
                
                command_prefix=PREFIX,
                owner_id=OWNER_ID,
                intents=Intents.all(),

            )
        
    def run(self, version):
        self.VERSION = version

        with open("./library/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True) #check if token is correct or use  token.0

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(1256577267413553222)
            print("bot ready")

        else:
            print("bot reconnected")
            

    async def on_message(self, message):
        pass

bot = Bot()