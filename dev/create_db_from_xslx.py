import sqlite3
import pandas as pd
from config import ROOT_DIR

df = pd.read_excel(ROOT_DIR / "LivsmedelsDB_202607110024.xlsx", skiprows=2)

df.columns = df.columns.str.replace(r"[(),]", "", regex=True)
df.columns = df.columns.str.replace(" ", "_")
df.columns = df.columns.str.replace("µ", "u")

with sqlite3.connect(ROOT_DIR / 'res/Livsmedelsverket.db') as conn:
    df.to_sql('livsmedelsverket', conn, if_exists='replace', index=True, index_label='id')

print('Database created')