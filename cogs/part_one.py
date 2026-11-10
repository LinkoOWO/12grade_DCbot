import json
import random
from pathlib import Path

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands


with Path(__file__).with_name("endlish_part1.json").open("r", encoding="utf-8") as file:
    exam = json.load(file)


def escape_display_text(value):
    text = discord.utils.escape_markdown(str(value))
    return discord.utils.escape_mentions(text)


class Part_1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
#ai
    @app_commands.command(name="mock_part_1", description="模考英文第一大題 共260題")
    @app_commands.choices(
        mode=[
            Choice(name="照順序", value=1),
            Choice(name="隨機", value=2),
        ]
    )
    async def examination_1(
        self,
        interaction: discord.Interaction,
        mode: Choice[int],
        open: int,
        quantity: int,
    ):
        total = len(exam)
        if open < 1 or open > total or quantity < 1 or quantity > total:
            await interaction.response.send_message(
                "只讓我吃青菜，還妄想我去買肉肉煮給你吃啊( `3′)",)
            return

        if mode.value == 1:
            if open + quantity - 1 > total:
                await interaction.response.send_message(
                    "只讓我吃青菜，還妄想我去買肉肉煮給你吃啊( `3′)")
                return
            question_ids = list(range(open, open + quantity))
        else:
            question_ids = random.sample(range(1, total + 1), quantity)

        view = self.PageView(question_ids, interaction.user.id)
        await interaction.response.send_message(embed=view.create_embed(), view=view)
        view.message = await interaction.original_response()

    class PageView(discord.ui.View):
        def __init__(self, question_ids, user_id):
            super().__init__(timeout=300)
            self.question_ids = question_ids
            self.user_id = user_id
            self.current_page = 0
            self.score = 0
            self.graded_count = 0
            self.message = None

        def create_embed(self):
            question_id = self.question_ids[self.current_page]
            question = exam[str(question_id)]
            embed = discord.Embed(title=f"第 {self.current_page + 1} 題")
            embed.add_field(
                name="\u200b",
                value=(
                    f"{escape_display_text(question['Q'])}\n"
                    f"A: {escape_display_text(question['A'])}\n"
                    f"B: {escape_display_text(question['B'])}\n"
                    f"C: {escape_display_text(question['C'])}\n"
                    f"D: {escape_display_text(question['D'])}\n\n\n"
                    f"題目序號: {question_id}\n"
                    f"年分: {question['year']}\n"
                    f"次序: {question['no']}"
                ),
                inline=False,
            )
            return embed

        async def submit_answer(self, interaction: discord.Interaction, answer: str):
            question_id = self.question_ids[self.current_page]
            question = exam[str(question_id)]
            correct_answer = str(question.get("Correct") or "").strip().upper()
            if correct_answer in {"A", "B", "C", "D"}:
                self.graded_count += 1
                is_correct = answer == correct_answer
                if is_correct:
                    self.score += 1
                    feedback = "答對了！"
                else:
                    correct_text = escape_display_text(question[correct_answer])
                    feedback = f"答錯了，正確答案是 {correct_answer}: {correct_text}。"
            else:
                feedback = "本題答案尚未建檔，無法判定正誤且不列入計分。"

            self.current_page += 1
            if self.current_page == len(self.question_ids):
                ungraded_count = len(self.question_ids) - self.graded_count
                result_description = (
                    f"Ciallo (∠・ω )⌒☆\n答對 {self.score} / {self.graded_count} 題。"
                    if self.graded_count
                    else "本次題目沒有可計分的答案。"
                )
                if ungraded_count:
                    result_description += f"\n另有 {ungraded_count} 題答案尚未建檔，不列入計分。"
                result_description += (
                    "\n本次測驗題目 ID（依序）："
                    + ", ".join(str(question_id) for question_id in self.question_ids)
                )
                result = discord.Embed(
                    title="模考完成",
                    description=result_description,
                )
                await interaction.response.edit_message(embed=result, view=None)
                await interaction.followup.send(
                    f"{feedback} 本次答對：{self.score} / {self.graded_count} 題",
                    ephemeral=True,
                )
                self.stop()
                return

            await interaction.response.edit_message(embed=self.create_embed(), view=self)
            await interaction.followup.send(
                f"{feedback} 目前答對：{self.score} / {self.graded_count} 題",
                ephemeral=True,
            )

        @discord.ui.button(label="A", style=discord.ButtonStyle.secondary)
        async def answer_a(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.submit_answer(interaction, "A")

        @discord.ui.button(label="B", style=discord.ButtonStyle.secondary)
        async def answer_b(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.submit_answer(interaction, "B")

        @discord.ui.button(label="C", style=discord.ButtonStyle.secondary)
        async def answer_c(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.submit_answer(interaction, "C")

        @discord.ui.button(label="D", style=discord.ButtonStyle.secondary)
        async def answer_d(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.submit_answer(interaction, "D")

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            if self.message is not None:
                await self.message.edit(view=self)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    "這不是你的模考題目。", ephemeral=True
                )
                return False
            return True


async def setup(bot):
    await bot.add_cog(Part_1(bot))
