#import area for DC bot cogs
import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
from discord.app_commands import Choice
import asyncio

#import area for main defnitions
import os
import sqlite3
import pandas as pd
import json
#import openpyxl
#import csv

#data tracking
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "english_data.db")

'''
with open("cogs\\ancient_chinese.json", "r", encoding="utf-8") as f:
    c_data = json.load(f)
'''

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
def is_admin():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_vocab",description="替資料庫新增單字.")
    async def write(self,interaction: discord.Interaction,file: discord.Attachment | None = None):

        def check(message):
            return (message.author == interaction.user and not message.author.bot and message.channel == interaction.channel)

        if file is not None:
            file_extension = os.path.splitext(file.filename)[1].lower()
            file_path = os.path.join(current_dir, os.path.basename(file.filename))
            try:
                await file.save(file_path)
                if file_extension == ".xlsx":
                    enter_file = pd.read_excel(file_path)
                elif file_extension == ".csv":
                    enter_file = pd.read_csv(file_path)
                else:
                    await interaction.response.send_message("不支援的檔案格式，請上傳 `.xlsx` 或 `.csv`。",ephemeral=True)
                    return
                print(enter_file.columns)
                enter_file.to_sql(name="english data",con=data,if_exists="append",index=False)
                await interaction.response.send_message("收件完畢( ˶ˆ꒳ˆ˵ ).")
            except Exception as e:
                await interaction.response.send_message(f"出錯啦(╥﹏╥): {e}",ephemeral=True)
            return
        await interaction.response.send_message(
            """
    請輸入單字架構：

    單字~等級~字首~字根~字尾~字根字首字尾~中文~ing-pt-pp~特殊用法~特殊用法中文~例句

    該欄位如果沒有資料請填入 0。

    輸入 0 可以取消。
    """,ephemeral=True)
        try:
            response_message = await self.bot.wait_for("message",check=check,timeout=60.0)
        except asyncio.TimeoutError:
            await interaction.followup.send("超過60秒不回我(￣へ￣) byebye~",ephemeral=True)
            return
        response = response_message.content.strip()
        if response == "0":
            await interaction.followup.send("呀? 沒事的話我要去玩啦(๑>◡<๑) byebye~")
            return
        try:
            word_list = response.split("~")
            if len(word_list) != 11:
                await interaction.followup.send(f"格式錯誤！\n"f"目前有 {len(word_list)} 個欄位，"f"應該要有 11 個欄位。",ephemeral=True)
                return
            
            word_tuple = tuple(word_list)

            insert_movement = """
                INSERT INTO [english data]
                (
                    單字,
                    等級,
                    字首,
                    字根,
                    字尾,
                    字根字首字尾,
                    中文,
                    [ing-pt-pp],
                    特殊用法,
                    特殊用法中文,
                    例句
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(insert_movement,word_tuple)
            data.commit()
            await interaction.followup.send("新增成功( ˶ˆ꒳ˆ˵ )！")
        except Exception as e:
            await interaction.followup.send(f"出錯啦(╥﹏╥): {e}",ephemeral=True)

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


    @app_commands.command(name="search_vocab_list",description="查看特定類型資料。查看[英文/全部/中文解釋]單字資料庫請在mode中選擇。")
    @app_commands.choices(
        mode=[
            Choice(name="英文", value=1),
            Choice(name="中文", value=2),
            Choice(name="全部", value=3)
        ],
        level=[
            Choice(name="不限", value="0"),
            Choice(name="L1", value="1"),
            Choice(name="L2", value="2"),
            Choice(name="L3", value="3"),
            Choice(name="L4", value="4"),
            Choice(name="L5", value="5"),
            Choice(name="L6", value="6"),
            Choice(name="其他", value="7")
        ]
    )
    async def check_and_show(
        self, interaction: discord.Interaction, level: Choice[str] = None, prefix: str = "0", root: str = "0", suffix: str = "0", mode: Choice[int] = None):

        level_value = level.value if level else "0"
        mode_value = mode.value if mode else 3

        condition = ""
        if level_value != "0":
            condition += f"等級='L{level_value}' AND "
        if prefix != "0":
            condition += f"字首='{prefix}' AND "
        if root != "0":
            condition += f"字根='{root}' AND "
        if suffix != "0":
            condition += f"字尾='{suffix}' AND "
        if not condition and mode_value != 3:
            await interaction.response.send_message(
                "倒是幫我買一套篩選器阿(`皿´)"
            )
            return

        if condition:
            condition = condition[:-5]

        def database_action():
            if condition:
                sql = f"SELECT * FROM [english data] WHERE {condition};"
            else:
                sql = "SELECT * FROM [english data];"
            print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

        def embed_creator(pages, current_page, total_pages, mode_mode):
            pagenow = pages[current_page - 1]
            embed = discord.Embed(title=f"查詢結果 ({current_page}/{total_pages})", color=0x3498db)

            for entry in pagenow:
                if mode_mode == 1:
                    n_value = (f"**ing-pt-pp**: {entry[8]}\n"f"**特殊用法**: {entry[9]}\n"f"**例句**: {entry[11]}")
                elif mode_mode == 2:
                    n_value = (f"**中文**: {entry[7]}\n"f"**字根字首字尾**: {entry[6]}\n"f"**特殊用法中文**: {entry[10]}")
                else:
                    n_value = (
                        f"**字首**: {entry[3]}\n"
                        f"**字根**: {entry[4]}\n"
                        f"**字尾**: {entry[5]}\n"
                        f"**字根字首字尾**: {entry[6]}\n"
                        f"**中文**: {entry[7]}\n"
                        f"**ing-pt-pp**: {entry[8]}\n"
                        f"**特殊用法**: {entry[9]}\n"
                        f"**特殊用法的中文**: {entry[10]}\n"
                        f"**例句**: {entry[11]}"
                        )
                embed.add_field(
                    name=f"ID:{entry[0]} {entry[1]} {entry[2]}",
                    value=n_value,
                    inline=False
                )
            return embed
        try:
            result = database_action()
            if not result:
                await interaction.response.send_message("空的O.O")
                return
            
            pages = [
                result[i:i + 5]
                for i in range(0, len(result), 5)
            ]
            total_pages = len(pages)
            current_page = 1
            output_embed = embed_creator(
                pages,
                current_page,
                total_pages,
                mode_value
            )
            view = self.PageView(
                pages,
                current_page,
                total_pages,
                mode_value,
                embed_creator
            )
            await interaction.response.send_message(
                embed=output_embed,
                view=view
            )

        except Exception as e:

            print("search_vocab_list 發生錯誤：")
            print(type(e).__name__, e)

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"發生錯誤：`{type(e).__name__}: {e}`"
                )

    @app_commands.command(name="search_one_vocab", description="尋找單一單字資料")
    async def check_one(self, interaction: discord.Interaction, word: str):
#       word = word.lower()
        cursor.execute(f"SELECT * FROM [english data] WHERE 單字 = '{word}';")
        result = cursor.fetchall()
        data.commit
        print(result)
        print(len(result))
        embed = discord.Embed(
            title=f"查詢結果",
            color=0x3498db
            )
        if not result:
            await interaction.response.send_message("空的O.O")
        try:
            embed.add_field(
                name=f"ID:{result[0][0]} {result[0][1]} {result[0][2]}",
                value=f"**字首**: {result[0][3]}\n**字根**: {result[0][4]}\n**字尾**: {result[0][5]}\n**字根字首字尾**: {result[0][6]}\n**中文**: {result[0][7]}\n**ing-pt-pp**: {result[0][8]}\n**特殊用法**: {result[0][9]}\n**特殊用法的中文**: {result[0][10]}\n**例句**: {result[0][11]}",
                inline=False
                )
            await interaction.response.send_message(embed=embed,)
            return
        except Exception as e:
            await interaction.response.send_message(f"出錯啦(╥﹏╥): {e}")

    @app_commands.command(name="data_pieces", description="確認最高id")
    async def check_index(self, interaction: discord.Interaction):
        cursor.execute("SELECT MAX(id) FROM [english data]")
        result = cursor.fetchone()
        await interaction.response.send_message(f"我超富有的好嘛.3. 有{result[0]}塊錢呢")
        print(f"目前資料庫最高id為: {result[0]}")

    @app_commands.command(name="delete_vocab", description="刪除單字資料")
    @is_admin()
    async def delete_vocab(self, interaction: discord.Interaction, id: int):
        cursor.execute(f"DELETE FROM [english data] WHERE id = {id};")
        data.commit()
        await interaction.response.send_message(f"已刪除ID為{id}的單字資料。")

    @app_commands.command(name="update_vocab", description="更新單字資料")
#   @is_admin()
    @app_commands.choices(
        field=[
            Choice(name="單字", value="單字"),
            Choice(name="等級", value="等級"),
            Choice(name="字首", value="字首"),
            Choice(name="字根", value="字根"),
            Choice(name="字尾", value="字尾"),
            Choice(name="字根字首字尾", value="字根字首字尾"),
            Choice(name="中文", value="中文"),
            Choice(name="ing-pt-pp", value="ing-pt-pp"),
            Choice(name="特殊用法", value="特殊用法"),
            Choice(name="特殊用法中文", value="特殊用法中文"),
            Choice(name="例句", value="例句")
        ]
    )
    async def update_vocab(self, interaction: discord.Interaction, id: int, field: Choice[str], new_value: str):
        field = field.value
        cursor.execute(f"UPDATE [english data] SET {field} = ? WHERE id = ?", (new_value, id))
        data.commit()
        await interaction.response.send_message(f"已更新ID為{id}的單字資料，欄位{field}已更改為{new_value}。")

    @app_commands.command(name="vocab_card", description="查看特定類型資料。查看[英文/全部/中文解釋]單字資料庫請在mode中選擇。")
    @app_commands.choices(
        level=[
            Choice(name="不限", value="0"),
            Choice(name="L1", value="1"),
            Choice(name="L2", value="2"),
            Choice(name="L3", value="3"),
            Choice(name="L4", value="4"),
            Choice(name="L5", value="5"),
            Choice(name="L6", value="6"),
            Choice(name="其他", value="7")
        ]
    )
    async def vocab_card(self, interaction: discord.Interaction, level: Choice[str] = None, prefix: str = "0", root: str = "0", suffix: str = "0", start_page: int = 1):
        level_value = level.value if level else "0"
        condition = ""

        if level_value != "0":
            condition += f"等級='L{level_value}' AND "
        if prefix != "0":
            condition += f"字首='{prefix}' AND "
        if root != "0":
            condition += f"字根='{root}' AND "
        if suffix != "0":
            condition += f"字尾='{suffix}' AND "
        if not condition:
            await interaction.response.send_message("倒是幫我買一套篩選器阿(`皿´)")
            return

        condition = condition[:-5]

        def database_action():
            sql = f"SELECT *FROM [english data] WHERE {condition};"
            cursor.execute(sql)
            return cursor.fetchall()
        
        def embed_creator(pages, current_page, total_pages):
            entry = pages[(current_page - 1) // 2]
            embed = discord.Embed(
                title=f"目前頁數 ({current_page}/{total_pages})",
                color=0x3498db
            )

            if current_page % 2 == 1:
                embed.add_field(
                    name=f"ID: {entry[0]}",
                    value=(
                        f"**等級**: {entry[2]}\n"
                        f"**單字**: {entry[1]}"
                    ),
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"ID: {entry[0]} {entry[1]}",
                    value=(
                        f"**中文**: {entry[7]}\n"
                        f"**特殊用法**: {entry[9]}\n"
                        f"**特殊用法的中文**: {entry[10]}\n"
                        f"**字根字首字尾**: {entry[6]}\n"
                    ),
                    inline=False
                )
            return embed
        try:
            result = database_action()
            if not result:
                await interaction.response.send_message("空的O.O")
                return
            
            pages = result
            total_pages = len(pages) * 2
            current_page = start_page
            if current_page < 1 or current_page > total_pages:
                await interaction.response.send_message(f"頁數超出範圍，請輸入介於 1 到 {total_pages} 的頁數。")
                return
            output_embed = embed_creator(
                pages,
                current_page,
                total_pages
            )
            view = self.PageView_for_Card(
                pages,
                current_page,
                total_pages,
                embed_creator
            )
            await interaction.response.send_message(embed=output_embed,view=view)

        except Exception as e:
            print("vocab_card 發生錯誤：")
            print(type(e).__name__, e)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"發生錯誤：`{type(e).__name__}: {e}`"
                )

    class PageView_for_Card(discord.ui.View):
        def __init__(self,pages,current_page,total_pages,embed_creator):
            super().__init__(timeout=60)
            self.pages = pages
            self.current_page = current_page
            self.total_pages = total_pages
            self.embed_creator = embed_creator

        @discord.ui.button(label="⬅️",style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.current_page > 1:
                self.current_page -= 1
                embed = self.embed_creator(self.pages,self.current_page,self.total_pages)
                await interaction.response.edit_message(embed=embed,view=self)
            else:
                await interaction.response.defer()

        @discord.ui.button(label="➡️",style=discord.ButtonStyle.secondary)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.current_page < self.total_pages:
                self.current_page += 1
                embed = self.embed_creator(self.pages,self.current_page,self.total_pages)
                await interaction.response.edit_message(embed=embed,view=self)
            else:
                await interaction.response.defer()

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
    
async def setup(bot):
    await bot.add_cog(DatabaseCog(bot))