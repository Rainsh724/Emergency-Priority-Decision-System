import sqlite3
import pandas as pd

conn = sqlite3.connect("data/epds.db")

# دیدن اسم جدول‌ها
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# دیدن داده‌ها
df = pd.read_sql_query("SELECT * FROM reports", conn)

print("\n📊 DATA:")
print(df)

print("\n📌 Last 5 rows:")
print(df.tail())

print("\n📌 Shape:", df.shape)

conn.close()