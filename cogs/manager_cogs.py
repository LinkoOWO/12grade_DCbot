import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
import asyncio

def is_admin():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="停止運行", description="叫這隻Yuri去睡覺...只能讓主人叫她睡覺喔~")
    @is_admin()
    async def shutdown(self, ctx):
        await ctx.send("晚安~ (｡･ω･｡)ﾉ♡")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Manager(bot))