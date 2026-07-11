import sqlite3
from dataclasses import dataclass

from config import ROOT_DIR
from rapidfuzz import fuzz

def fuzzy_match(query:str, db_value:str):
    query = query.lower().strip()
    db_value = db_value.lower().strip()
    return fuzz.WRatio(query, db_value)

# Assigns higher values to db_values with full query as substr and that start or end with query
def advanced_fuzzy_match(query:str, db_value:str):
    query = query.lower().strip()
    db_value = db_value.lower().strip()

    base_score = fuzz.WRatio(query, db_value)

    # Prioritize items that start or end with query
    if db_value.startswith(query) or db_value.endswith(query):
        base_score += 20
    # Prioritize items with exact query as substr
    if f" {query} " in db_value:
        base_score += 10

    return base_score

class LivsmedelsverketClient:
    def __init__(self):
        self.livsmedelsverket_conn = sqlite3.connect(ROOT_DIR / 'res/livsmedelsverket.db')
        self.livsmedelsverket_conn.row_factory = sqlite3.Row
        self.livsmedelsverket_conn.create_function('FUZZ', 2, fuzzy_match)
        self.livsmedelsverket_conn.create_function('ADV_FUZZ', 2, advanced_fuzzy_match)

    def get_food_by_id(self, id):
        with self.livsmedelsverket_conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livsmedelsverket WHERE id = ?", (id,))
            return cursor.fetchone()

    def get_food_by_number(self, number):
        with self.livsmedelsverket_conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livsmedelsverket WHERE Livsmedelsnummer = ?", (number,))
            return cursor.fetchone()

    def get_food_by_name(self, name):
        with self.livsmedelsverket_conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livsmedelsverket WHERE Livsmedelsnamn = ?", (name,))
            return cursor.fetchone()

    def search_foods_by_name(self, query, limit=20):
        with self.livsmedelsverket_conn as conn:
            sql = """
            SELECT *, ADV_FUZZ(?, Livsmedelsnamn) as score
            FROM livsmedelsverket
            WHERE score >= 70
            ORDER BY score DESC
            LIMIT ?
            """

            cursor = conn.cursor()
            cursor.execute(sql, (query, limit))
            return [dict(row) for row in cursor.fetchall()]