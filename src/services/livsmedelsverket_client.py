import sqlite3
from config import ROOT_DIR


class LivsmedelsverketClient:
    def __init__(self):
        self.livsmedelsverket_conn = sqlite3.connect(ROOT_DIR / 'res/livsmedelsverket.db')
        self.livsmedelsverket_conn.row_factory = sqlite3.Row

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
            cursor.execute("SELECT * FROM livsmedelsverket WHERE Livsmedelsname = ?", (name,))
            return cursor.fetchone()

