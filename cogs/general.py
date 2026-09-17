import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
import asyncio

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="敲一下Yuri的頭 看看睡起來差了多久時間")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"啊啊啊會痛的啦(╥﹏╥). 你要的時差是{round(self.bot.latency * 1000)}ms啦")

async def setup(bot):
    await bot.add_cog(General(bot))