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

class Ingredient:
    def __init__(self, item_id:int, name:str, protein: float, fat: float, carbs: float, calories: float, groups: list | None = None, micronutrients: dict | None = None):
        self.id = item_id
        self.name = name
        self.protein = protein
        self.fat = fat
        self.carbs = carbs
        self.calories = calories

        self.groups = groups if groups is not None else []
        self.micronutrients = micronutrients if micronutrients is not None else {}

    @staticmethod
    def from_livsmedelsverket_dict(db_dict: dict | sqlite3.Row):
        data = dict(db_dict).copy()

        ing_id = int(data.pop("id"))
        ingredient_name = str(data.pop("Food_Name"))
        protein = float(data.pop("Protein_g"))
        fat = float(data.pop("Fat_total_g"))
        carbs = float(data.pop("Carbohydrates_available_g"))
        calories = int(data.pop("Energy_kcal"))
        groups = [s.strip() for s in str(data.pop("Filter_group")).split(",")]

        micronutrients = {k: float(v) if v is not None else None for k, v in data.items()}

        return Ingredient(ing_id, ingredient_name, protein, fat, carbs, calories, groups, micronutrients)


class LivsmedelsverketClient:
    def __init__(self):
        self.livsmedelsverket_conn = sqlite3.connect(ROOT_DIR / 'res/livsmedelsverket.db')
        self.livsmedelsverket_conn.row_factory = sqlite3.Row
        self.livsmedelsverket_conn.create_function('FUZZ', 2, fuzzy_match)
        self.livsmedelsverket_conn.create_function('ADV_FUZZ', 2, advanced_fuzzy_match)

    def get_food_by_id(self, db_id):
        with self.livsmedelsverket_conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livsmedelsverket WHERE id = ?", (db_id,))
            return cursor.fetchone()

    def get_food_by_number(self, number):
        with self.livsmedelsverket_conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livsmedelsverket WHERE Food_Number = ?", (number,))
            return cursor.fetchone()

    def get_food_by_name(self, name):
        with self.livsmedelsverket_conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livsmedelsverket WHERE Food_Name = ?", (name,))
            return cursor.fetchone()

    def search_foods_by_name(self, query, limit=20):
        with self.livsmedelsverket_conn as conn:
            sql = """
            SELECT *, ADV_FUZZ(?, Food_Name) as score
            FROM livsmedelsverket
            WHERE score >= 70
            ORDER BY score DESC
            LIMIT ?
            """

            cursor = conn.cursor()
            cursor.execute(sql, (query, limit))
            return [dict(row) for row in cursor.fetchall()]