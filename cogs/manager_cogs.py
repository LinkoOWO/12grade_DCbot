import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
import asyncio

import os
import sys

def is_admin():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shutdown", description="叫這隻Yuri去睡覺...只能讓主人叫她睡覺喔~")
    @is_admin()
    async def shutdown(self, interaction: discord.Interaction):
        await interaction.response.send_message("晚安~ (｡･ω･｡)ﾉ♡")
        await self.bot.close()

    '''@app_commands.command(name="restart", description="叫這隻Yuri去重啟...只能讓主人叫她重啟喔~")
    @is_admin()
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.send_message("重啟中... (｡･ω･｡)ﾉ♡")
        await self.bot.close()
        os.execv(sys.executable, ['python'] + sys.argv)'''

    @app_commands.command(name="cog_upload", description="穿裝備啦~(載入一個 Cog)（限管理員）")
    @is_admin()
    async def load_cog(self, interaction: discord.Interaction, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"好耶是大佬裝(((o(*ﾟ▽ﾟ*)o))) `{cog}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"沒機緣了(╥﹏╥) {e}", ephemeral=True)

    @app_commands.command(name="cog_unload", description="噴裝啦(╥﹏╥) (卸載一個 Cog)（限管理員）")
    @is_admin()
    async def unload_cog(self, interaction: discord.Interaction, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"只有新手裝了(╥﹏╥)", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"想打敗我( ꜆⌯'▾'⌯)꜆ 先練個3000年吧( ｰ̀֊ｰ́ )✧ {e}", ephemeral=True)

    @app_commands.command(name="cog_reload", description="把裝備洗了再穿啦~(重新載入一個 Cog)（限管理員）")
    @is_admin()
    async def reload_cog(self, interaction: discord.Interaction, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"洗完啦~ Cog: `{cog}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"洗衣機壞了(╥﹏╥) {e}", ephemeral=True)

    @app_commands.command(name="listcog", description="列出 cogs 資料夾中的所有 .py 檔案（限管理員）")
    @is_admin()
    async def list_cogs(self, interaction: discord.Interaction):
        cog_folder = "cogs"
        cogs = [f[:-3] for f in os.listdir(cog_folder) if f.endswith(".py") and f != "__init__.py"]
        if not cogs:
            await interaction.response.send_message("空的O.O", ephemeral=True)
        else:
            formatted = "\n".join([f"`{c}`" for c in cogs])
            await interaction.response.send_message(f"打包完啦(๑¯∀¯๑):\n{formatted}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Manager(bot))