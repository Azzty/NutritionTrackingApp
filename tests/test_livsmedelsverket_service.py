import pytest
import src.services.livsmedelsverket_client as livsmedelsverket


def test_get_valid_food_number():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_number(1)
    assert food is not None and food["Livsmedelsnamn"] == "Nöt talg"

def test_get_food_number_out_of_range():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_number(2 ** 32 - 1)
    assert food is None

def test_get_invalid_food_number():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_number(-1)
    assert food is None

def test_get_valid_food_name():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_name("Nöt talg")
    assert food is not None and food["Livsmedelsnummer"] == 1

def test_get_invalid_food_name():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_name("")
    assert food is None

def test_get_valid_food_id():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_id(0)
    assert food is not None and food["Livsmedelsnamn"] == "Nöt talg"

def test_get_invalid_food_id():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_id(-1)
    assert food is None

def test_reasonable_results_from_search():
    client = livsmedelsverket.LivsmedelsverketClient()
    results = client.search_foods_by_name("mjölk", 5)
    assert any(d.get("Livsmedelsnamn") == "Mjölk fett 3% berikad" for d in results)
    assert any(d.get("Livsmedelsnamn") == "Mjölk fett 4,2% typ lantmjölk" for d in results)

def test_fuzzy_match_tolerance():
    score = livsmedelsverket.fuzzy_match("Mjlk", "Mjölk")
    assert score > 70

def test_fuzzy_match_case_insensitive():
    upper_score = livsmedelsverket.fuzzy_match("MJÖLK", "mjölk")
    lower_score = livsmedelsverket.fuzzy_match("mjölk", "mjölk")
    assert upper_score == lower_score
