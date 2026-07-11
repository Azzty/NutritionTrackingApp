import pytest
import src.services.livsmedelsverket_client as livsmedelsverket


def test_get_valid_food():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food(1)
    assert food["Livsmedelsnamn"] == "Nöt talg"

def test_get_food_out_of_range():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food(2**32-1)
    assert food is None

def test_get_invalid_food():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food(-1)
    assert food is None