import sqlite3
from text_unidecode import unidecode

from src.config import ROOT_DIR
from rapidfuzz import fuzz


def fuzzy_match(query: str, db_value: str):
    query = query.lower().strip()
    db_value = db_value.lower().strip()
    return fuzz.WRatio(query, db_value)


# Smarter search for more intuitive results
def advanced_fuzzy_match(query: str, db_name: str, db_group: str | None = None):
    if query is None or db_name is None or query == "":
        return 0

    query = unidecode(query.lower().strip())
    db_name = unidecode(db_name.lower().strip())
    db_group = unidecode(db_group.lower().strip()) if db_group is not None else ""

    query_words = query.split()
    db_name_words = set(db_name.split())
    db_group_words = set(db_group.split())

    base_score = fuzz.WRatio(query, db_name)

    # Boost items that start with word in query
    if any(db_name.startswith(word) for word in query_words):
        base_score += 20
    # Boost items that end with query
    if any(db_name.endswith(word) for word in query_words):
        base_score += 10
    # Boost items with all query words as substr
    if all(word in db_name_words for word in query_words):
        base_score += 15
    # Boost items with associated group in query
    if any(word in db_group_words for word in query_words):
        base_score += 70

    return base_score


class Ingredient:
    def __init__(
        self,
        item_id: int,
        name: str,
        protein: float,
        fat: float,
        carbs: float,
        calories: float,
        food_number: int | None = None,
        groups: list | None = None,
        micronutrients: dict | None = None,
    ):
        self.id = item_id
        self.name = name
        self.protein = protein
        self.fat = fat
        self.carbs = carbs
        self.calories = calories

        self.food_number = food_number if food_number else None
        self.groups = groups if groups is not None else []
        self.micronutrients = micronutrients if micronutrients is not None else {}

    @staticmethod
    def from_livsmedelsverket_dict(db_dict: dict | sqlite3.Row):
        if db_dict is None:
            return None
        data = dict(db_dict).copy()

        ing_id = int(data.pop("id"))
        ingredient_name = str(data.pop("Food_Name"))
        protein = float(data.pop("Protein_g"))
        fat = float(data.pop("Fat_total_g"))
        carbs = float(data.pop("Carbohydrates_available_g"))
        calories = int(data.pop("Energy_kcal"))
        groups = [s.strip() for s in str(data.pop("Filter_group")).split(",")]
        food_number = int(data.pop("Food_Number"))

        micronutrients = {
            k: float(v) if v is not None else None for k, v in data.items()
        }

        return Ingredient(
            ing_id,
            ingredient_name,
            protein,
            fat,
            carbs,
            calories,
            food_number=food_number,
            groups=groups,
            micronutrients=micronutrients,
        )


class LivsmedelsverketClient:
    def __init__(self):
        self.livsmedelsverket_conn = sqlite3.connect(
            ROOT_DIR / "res/livsmedelsverket.db"
        )
        self.livsmedelsverket_conn.row_factory = sqlite3.Row
        self.livsmedelsverket_conn.create_function(
            "FUZZ", 2, fuzzy_match, deterministic=True
        )
        self.livsmedelsverket_conn.create_function(
            "ADV_FUZZ", 3, advanced_fuzzy_match, deterministic=True
        )

    def get_food_by_id(self, db_id) -> Ingredient:
        with self.livsmedelsverket_conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livsmedelsverket WHERE id = ?", (db_id,))
            return Ingredient.from_livsmedelsverket_dict(cursor.fetchone())

    def get_food_by_number(self, number) -> Ingredient:
        with self.livsmedelsverket_conn as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM livsmedelsverket WHERE Food_Number = ?", (number,)
            )
            return Ingredient.from_livsmedelsverket_dict(cursor.fetchone())

    def get_food_by_name(self, name) -> Ingredient:
        with self.livsmedelsverket_conn as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM livsmedelsverket WHERE Food_Name = ?", (name,)
            )
            return Ingredient.from_livsmedelsverket_dict(cursor.fetchone())

    def search_foods_by_name(self, query, limit=20) -> list[Ingredient]:
        with self.livsmedelsverket_conn as conn:
            sql = """
                  SELECT *
                  FROM (SELECT *, ADV_FUZZ(?, Food_Name, Filter_group) as score
                        FROM livsmedelsverket)
                  WHERE score >= 70
                  ORDER BY score DESC LIMIT ? \
                  """

            cursor = conn.cursor()
            cursor.execute(sql, (query, limit))
            return [
                Ingredient.from_livsmedelsverket_dict(row) for row in cursor.fetchall()
            ]
