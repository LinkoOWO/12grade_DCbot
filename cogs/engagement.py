import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
import asyncio

import random
import numpy as np

class Engagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="random_number", description="範圍內隨機取整數")
    async def random_number(self, interaction: discord.Interaction, minimum: int, maximum: int, amount: int = 1):
        try:
            response_n = ""
            sample = random.sample(range(minimum, maximum + 1), amount)
            sample.sort(reverse=True)
            response_n += " ".join(map(str, sample))
            print(response_n)
            await interaction.response.send_message(f"抽完啦(๑>◡<๑) 抽到了{response_n}")
        except Exception as e:
            await interaction.response.send_message(f"出錯啦(╥﹏╥): {e}")

    @app_commands.command(name="guess_dice", description="骰子比大小")
    async def random_dice(self, interaction: discord.Interaction, guess: str):
        return

    @app_commands.command(name="tri_functions", description="6大三角函數 hypo斜oppo對adja鄰 請輸入直角三角形")
    async def trigonometric_functions(self, interaction: discord.Interaction, hypotenuse: int, opposite: int, adjacent: int, degree: int, radium: int):
        def right_triangle(x: int, y: int, z:int):
            hypo = max(x, y, z)
            if hypo == x:
                if hypo^2 == y^2+z^2:
                    return True
            elif hypo == y:
                if hypo^2 == x^2+z^2:
                    return True
            elif hypo == z:
                if hypo^2 == x^2+y^2:
                    return True
            else:
                return False
        def cos_func_sides(a, b, c):
            cos_a = ((b**2+c**2-a**2)/2*b*c)**0.5
            cos_b = ((a**2+c**2-b**2)/2*a*c)**0.5
            cos_c = ((a**2+b**2-c**2)/2*a*b)**0.5
            l_cos = [cos_a, cos_b, cos_c]
            return l_cos

async def setup(bot):
    await bot.add_cog(Engagement(bot))