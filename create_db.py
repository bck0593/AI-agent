import sqlite3
from datetime import datetime, timedelta
import random
import os

# --- ここでファイル削除（ファイルがあれば消す） ---
if os.path.exists('db.sqlite3'):
    os.remove('db.sqlite3')
# ------------------------------------------------------

# SQLiteに接続（新しいファイルが作られる）
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

# --- ここで必ず古いテーブルを消す！ ---
c.execute('DROP TABLE IF EXISTS transactions')
# -----------------------------------------

# テーブル作成（今の正しい形で）
c.execute('''
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    amount REAL,
    type TEXT,
    description TEXT
)
''')

# サンプルデータ作成
types = ['給与', '食費', '光熱費', 'ATM引き出し', '娯楽費', '交通費','通信費','保険']
descriptions = {
    '給与': '会社からの給与',
    '食費': 'コンビニで購入',
    '光熱費': '電気代の支払い',
    'ATM引き出し': 'ATM現金引き出し',
    '娯楽費': '飲み会',
    '交通費': '電車代',
    '通信費':'携帯代',
    '保険':'保険代'
}

today = datetime.now()

data = []

for i in range(30):
    day = today - timedelta(days=i)
    if day.day == 1:
        data.append((
            day.strftime("%Y-%m-%d"),
            random.randint(250000, 300000),
            '給与',
            descriptions['給与']
        ))
    else:
        expense_type = random.choice(types[1:])
        amount = random.randint(500, 10000)
        data.append((
            day.strftime("%Y-%m-%d"),
            -amount,
            expense_type,
            descriptions[expense_type]
        ))

# データをDBに挿入
c.executemany('''
INSERT INTO transactions (date, amount, type, description)
VALUES (?, ?, ?, ?)
''', data)

conn.commit()
conn.close()

print("SQLite DB作成完了！")
