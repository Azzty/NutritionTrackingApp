import sqlite3
import pandas as pd
from pandas import read_excel

from config import ROOT_DIR

df = pd.read_excel(ROOT_DIR / "mat_SV.xlsx", skiprows=2)
df.columns = read_excel(ROOT_DIR / "mat_EN.xlsx", nrows=1, skiprows=2).columns

df.columns = df.columns.str.replace(r"[(),]", "", regex=True)
df.columns = df.columns.str.replace(" ", "_")
df.columns = df.columns.str.replace("µ", "u")

with sqlite3.connect(ROOT_DIR / 'res/Livsmedelsverket.db') as conn:
    df.to_sql('livsmedelsverket', conn, if_exists='replace', index=True, index_label='id')

print('Database created')