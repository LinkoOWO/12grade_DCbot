#import external extensions
from quart import Quart
import os
import discord
from discord.ext import commands
import asyncio
import json

#import internal extensions

#variables definition area
token="" #DC bot token

#open info file
with open("info.json", "r", encoding="utf-8") as f:
    info=json.load(f)

#app instance
app = Quart(__name__)

@app.route("/")
async def open():
    return "Website is alive."

async def run():
    port = int(os.environ.get("PORT", 8080))
    await app.run_task(host="0.0.0.0", port=port)

#terminal definition area(DC)
intents = discord.Intents.all()

class Bot(commands.Bot):
    #initial setting of the bot object
    #"self" is some of the object's default attributes.
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents, application_id=info["applicationID"])
    #below is to load cogs files if existing
    async def setup_hook(self):
        await self.load_extension("cogs.database_cogs_123xyz")

        await self.tree.sync()
        print("已同步指令至Discord伺服器.")
    
bot = Bot()

@bot.event
async def on_ready():
    print(f"Bot已啟動 登入為 {bot.user} (ID: {bot.user.id})")

#start (run if the file is original and not imported)
async def main():
    try:
        token = os.environ.get("token")
    except KeyError:
        try:
            token = info["token"]
        except KeyError:
            print("Error: 無法在控制台或info.json取得有效token.")
            return

    await asyncio.gather(
        run(),
        Bot().start(token)
    )

if __name__ == "__main__":
    asyncio.run(main())