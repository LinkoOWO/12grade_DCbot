import os
import sqlite3
import pandas as pd

#資料追蹤
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "english_data.db")

#建立資料與連接端
data = sqlite3.connect(db_path)
cursor=data.cursor()

#寫架構

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS [english data](
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
    例句 VARCHAR)
    """
    )
data.commit()

#寫入資料

def write():
    mode=str(input('輸入類型(檔案/單字)'))
    if mode=='檔案': #excel檔案匯入
            file=str(input('excel的檔名:'))
            file_path=os.path.join(current_dir,f"{file}.xlsx")
            enter_file=pd.read_excel(file_path)
            print(enter_file.columns)
            enter_file.to_sql(
                name='english data',
                con=data,
                if_exists="append",
                index=False
            )

    elif mode=='單字':
        print('架構:單字~等級~字首~字根~字尾~字根字首字尾(含中文)~中文(含詞性)~ing-pt-pp~特殊用法~特殊用法的中文~例句`該欄位如果沒有資料請填入0')
        word=str(input('單字(須符合結構)'))
        word_list=[]
        word_list=word.split('~')
        word_tuple=tuple(word_list)
        insert_movement="INSERT INTO [english data] (單字,字首,字根,字尾,字根字首字尾(含中文),中文(含詞性),ing-pt-pp,特殊用法,特殊用法的中文,例句) VALUES(?,?,?,?,?,?,?,?,?,?)"
        cursor.execute(insert_movement,word_tuple) 

    else:
        print('格式錯誤')
    data.commit()
    return

def check_and_show():
    type=str(input('查看特定類型資料(count)或全部資料(all)[請輸入提示詞]'))
    movement=str
    if type=='all':
        movement="CREATE VIEW IF NOT EXISTS [data view]AS SELECT * FROM [english data];"
        cursor.execute(movement)
    elif type =='count':
        print('指定id類型表')
        kind=str(input('請問你要哪些類型(等級~字首~字根~字尾)[使用~連接][再要求的內容格填入想要搜尋的內容,如果沒有要求請填0]#等級請寫L數字'))
        kind=kind.split('~')
        condition_sum=str
        group1="單字, [ing-pt-pp], 特殊用法, 例句"
        group2="中文, 字根字首字尾, 特殊用法中文"
        l=0
        for i in range(4):
            if kind[i]!="0":
                l+=1
                if i==0:
                    condition="等級 LIKE "
                elif i==1:
                    condition="字首 LIKE "
                elif i==2:
                    condition="字根 LIKE "
                else:
                    condition="字尾 LIKE "
                condition_sum=condition_sum+condition+kind[i]+' AND '
        if l!=0:
            condition_sum=condition_sum[:-5]
        else:
            condition_sum=""
        if condition_sum=="":
            movement1=f"CREATE VIEW [showcase data] AS SELECT {str(group1)} FROM [english data];"
            movement2=f"CREATE VIEW [answer data] AS SELECT {str(group2)} FROM [english data];"
        else:
            movement1=f"CREATE VIEW [showcase data] AS SELECT {str(group1)} FROM [english data] WHERE {str(condition_sum)};"
            movement2=f"CREATE VIEW [answer data] AS SELECT {str(group2)} FROM [english data] WHERE {str(condition_sum)};"
        print(movement1)
        cursor.execute(movement1)
        cursor.execute(movement2)
    else:
        print('格式錯誤')
    
    data.commit()
    return

def delete():
    mode=str(input('刪除資料(整個資料庫或資料)')) 

    if mode=='資料':
        type=str(input('哪種資料類型或哪筆資料(請使用AND(要大寫)連結)又或是全部資料(保留格式請選all):'))
        if type=='all':
            movement="DELETE FROM [english data];"
        #else還要再處理
            
        cursor.execute(movement)
        
    elif mode == '整個':
        cursor.execute(
            """
            DROP TABLE IF EXISTS [english data];
            """
        )

    else:
        print('格式錯誤')
    
    data.commit()
    return

execution=str(input('歡迎使用者使用本單字庫，請問要執行哪個功能呢(寫入、刪除、背單字)'))

if execution=='寫入':
    write()
elif execution=='刪除':
    delete()
elif execution=='單字':
    check_and_show()
    selection=str
    k=0
    while selection !='fin':
        first=pd.read_sql('SELECT * FROM [showcase data]', data)
        second=pd.read_sql('SELECT * FROM [answer data]', data)
        print(first.iloc[k])
        str(input('繼續請按enter'))
        print(second.iloc[k])
        selection=str(input('是否終止,是請打fin'))
        k+=1

cursor.execute('DROP VIEW IF EXISTS [showcase data];')
cursor.execute('DROP VIEW IF EXISTS [answer data];')
data.commit()
data.close()