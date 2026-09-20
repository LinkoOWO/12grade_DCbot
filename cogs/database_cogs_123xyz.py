#import area for DC bot cogs
import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
import asyncio

#import area for main defnitions
import os
import sqlite3
import pandas as pd
#import openpyxl
#import csv

#data tracking
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "english_data.db")

#construction of database
data = sqlite3.connect(db_path)
cursor=data.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS [english data](
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    單字 VARCHAR,
    等級 VARCHAR,
    字首 VARCHAR,
    字根 VARCHAR,
    字尾 VARCHAR,
    字根字首字尾 VARCHAR,
    中文 VARCHAR,
    [ing-pt-pp] VARCHAR,
    特殊用法 VARCHAR,
    特殊用法中文 VARCHAR,
    例句 VARCHAR
    )
    """
)
data.commit()

#functions
#bot setting
class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_vocab", description="替資料庫新增單字.")
    async def write(self, interaction: discord.Interaction, file: discord.Attachment = None):
        #check whether the message is from the user who is using the command.
        def check(message):
            return message.author == interaction.user and not message.author.bot and message.channel == interaction.channel
        #await interaction.response.send_message("請輸入操作的類型(1:檔案 2:單字):")
        #mode = int(await self.bot.wait_for("message", check=check, timeout=60.0))
        if file is not None:
            file_extension = os.path.splitext(file.filename)[1]
            if file_extension == ".xlsx":
                #AI generated
                file_path = os.path.join(current_dir, file.filename)
                await file.save(file_path)
                enter_file = pd.read_excel(file_path)
                print(enter_file.columns)
                enter_file.to_sql(
                    name='english data',
                    con=data,
                    if_exists="append",
                    index=False
                )
                await interaction.response.send_message("收件完畢( ˶ˆ꒳ˆ˵ ).")
            elif file_extension == ".csv":
                #AI generated
                file_path = os.path.join(current_dir, file.filename)
                await file.save(file_path)
                enter_file = pd.read_csv(file_path)
                print(enter_file.columns)
                enter_file.to_sql(
                    name='english data',
                    con=data,
                    if_exists="append",
                    index=False
                )
                await interaction.response.send_message("收件完畢( ˶ˆ꒳ˆ˵ ).")
            else:
                await interaction.response.send_message(
                    """
                請輸入單字架構
                架構:單字~等級~字首~字根~字尾~字根字首字尾(含中文)~中文(含詞性)~ing-pt-pp~特殊用法~特殊用法的中文~例句`該欄位如果沒有資料請填入0
                """,
                    ephemeral=True,
                )
                response_message = await self.bot.wait_for("message", check=check, timeout=60.0)
                if response_message == "0":
                    await interaction.response.send_message("呀? 沒事的話我要去玩啦(๑>◡<๑) byebye~")
                    return
                else:
                    try:
                        word_list=[]
                        word_list=response_message.split("~")
                        word_tuple=tuple(word_list)
                        insert_movement="INSERT INTO [english data] (單字,字首,字根,字尾,字根字首字尾(含中文),中文(含詞性),ing-pt-pp,特殊用法,特殊用法的中文,例句) VALUES(?,?,?,?,?,?,?,?,?,?)"
                        cursor.execute(insert_movement,word_tuple) 
                        data.commit()
                    except Exception as e:
                        await interaction.response.send_message(f"出錯啦(╥﹏╥): {e}")
                        return
    class PageView(discord.ui.View):
        def __init__(self,pages,current_page,total_pages,mode,embed_creator):
            super().__init__(timeout=60)
            self.pages = pages
            self.current_page = current_page
            self.total_pages = total_pages
            self.mode = mode
            self.embed_creator = embed_creator

        @discord.ui.button(label="⬅️",style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.current_page > 1:
                self.current_page -= 1
                embed = self.embed_creator(self.pages,self.current_page,self.total_pages,self.mode)
                await interaction.response.edit_message(embed=embed,view=self)
            else:
                await interaction.response.defer()

        @discord.ui.button(label="➡️",style=discord.ButtonStyle.secondary)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.current_page < self.total_pages:
                self.current_page += 1
                embed = self.embed_creator(self.pages,self.current_page,self.total_pages,self.mode)
                await interaction.response.edit_message(embed=embed,view=self)
            else:
                await interaction.response.defer()

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True

    @app_commands.command(name="search_vocab", description="查看特定類型資料. 查看[英文/全部/中文解釋]單字資料庫請在mode中打上[1/2/3].")
    async def check_and_show(self, interaction: discord.Interaction, level: str = "0", prefix: str = "0", root: str = "0", suffix: str = "0", mode: int = 3):
        condition:str = ""
        if level != "0":
            condition += f"等級='L{level}' AND "
        if prefix != "0":
            condition += f"字首='{prefix}' AND "
        if root != "0":
            condition += f"字根='{root}' AND "
        if suffix != "0":
            condition += f"字尾='{suffix}' AND "

        if not condition and mode != 3:
            await interaction.response.send_message("倒是幫我買一套篩選器阿(`皿´)")
            return
        if condition:
            # Remove the lasting " AND "
            condition = condition[:-5]
            def mode_actionEnglish():
                movement1=f"SELECT * FROM [english data] WHERE {str(condition)};"
                print(movement1)
                cursor.execute(movement1)
                result1 = cursor.fetchall()
                data.commit()
                return result1
            def mode_actionChinese():
                movement2=f"SELECT * FROM [english data] WHERE {str(condition)};"
                print(movement2)
                cursor.execute(movement2)
                result2 = cursor.fetchall()
                data.commit()
                return result2
            def default_action():
                movement3=f"SELECT * FROM [english data] WHERE {str(condition)};"
                print(movement3)
                cursor.execute(movement3)
                result3 = cursor.fetchall()
                data.commit()
                return result3
            def embed_creator(pages, current_page, total_pages, mode_mode):
                pagenow = pages[current_page - 1]
                embed = discord.Embed(
                    title=f"查詢結果 ({current_page}/{total_pages})",
                    color=0x3498db
                    )
                for entry in pagenow:
                    if mode_mode == 1:
                        n_value = f"**ing-pt-pp**: {entry[8]}\n**特殊用法**: {entry[9]}\n**例句**: {entry[11]}"
                    elif mode_mode == 2:
                        n_value = f"**中文**: {entry[7]}\n**字根字首字尾**: {entry[6]}\n**特殊用法中文**: {entry[10]}"
                    else:
                        n_value = f"**字首**: {entry[3]}\n**字根**: {entry[4]}\n**字尾**: {entry[5]}\n**字根字首字尾**: {entry[6]}\n**中文**: {entry[7]}\n**ing-pt-pp**: {entry[8]}\n**特殊用法**: {entry[9]}\n**特殊用法的中文**: {entry[10]}\n**例句**: {entry[11]}"
                    embed.add_field(
                        name=f"ID:{entry[0]} {entry[1]} {entry[2]}",
                        value=n_value,
                        inline=False
                        )
                return embed
            try:
                if mode == 1:
                    result = mode_actionEnglish()
                    if not result:
                        await interaction.response.send_message("空的O.O")
                        return
                    pages = [result[i:i + 10] for i in range(0, len(result), 10)]
                elif mode == 2:
                    result = mode_actionChinese()
                    if not result:
                        await interaction.response.send_message("空的O.O")
                        return
                    pages = [result[i:i + 10] for i in range(0, len(result), 10)]
                elif mode == 3:
                    result = default_action()
                    if not result:
                        await interaction.response.send_message("空的O.O")
                        return
                    pages = [result[i:i + 10] for i in range(0, len(result), 10)]
                else:
                    await interaction.response.send_message("打錯東西啦(๑¯∀¯๑)，請輸入正確的模式(1:英文 2:中文 3:全部).")
                    return
                total_pages = len(pages)
                current_page = 1
                output_embed = embed_creator(pages, current_page, total_pages, mode)
                view = self.PageView(pages, current_page, total_pages, mode, embed_creator)

                await interaction.response.send_message(embed=output_embed,view=view,)
            except Exception as e:
                print("search_vocab 發生錯誤：")
                print(type(e).__name__, e)
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"發生錯誤：`{type(e).__name__}: {e}`")
        return

    @app_commands.command(name="vocab_card", description="生成單字卡")
    async def generate_flashcards(self, interaction: discord.Interaction, level: str = "0", prefix: str = "0", root: str = "0", suffix: str = "0"):
        pass
    
async def setup(bot):
    await bot.add_cog(DatabaseCog(bot))