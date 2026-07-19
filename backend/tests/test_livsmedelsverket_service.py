import src.services.livsmedelsverket_client as livsmedelsverket
import time


def test_get_valid_food_number():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_number(1)
    assert food is not None and food.name == "Nöt talg"


def test_get_food_number_out_of_range():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_number(2**32 - 1)
    assert food is None


def test_get_invalid_food_number():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_number(-1)
    assert food is None


def test_get_valid_food_name():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_name("Nöt talg")
    assert food is not None and food.id == 0


def test_get_invalid_food_name():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_name("")
    assert food is None


def test_get_valid_food_id():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_id(0)
    assert food is not None and food.name == "Nöt talg"


def test_get_invalid_food_id():
    client = livsmedelsverket.LivsmedelsverketClient()
    food = client.get_food_by_id(-1)
    assert food is None


def test_reasonable_results_from_search():
    client = livsmedelsverket.LivsmedelsverketClient()
    results = client.search_foods_by_name("mjölk", 5)
    assert any(ing.name == "Mjölk fett 3% berikad" for ing in results)
    assert any(ing.name == "Mjölk fett 4,2% typ lantmjölk" for ing in results)


def test_fuzzy_match_tolerance():
    score = livsmedelsverket.fuzzy_match("Mjlk", "Mjölk")
    assert score > 70


def test_fuzzy_match_case_insensitive():
    upper_score = livsmedelsverket.fuzzy_match("MJÖLK", "mjölk")
    lower_score = livsmedelsverket.fuzzy_match("mjölk", "mjölk")
    assert upper_score == lower_score


def test_advanced_fuzzy_match_no_filter():
    res = livsmedelsverket.advanced_fuzzy_match(
        "pannkaka", "Pannkaka tunn hemlagad", None
    )
    assert res


# noinspection PyTypeChecker
def test_advanced_fuzzy_match_empty_query():
    res = livsmedelsverket.advanced_fuzzy_match("", None)
    assert res == 0


def test_advanced_fuzzy_match_case_insensitive():
    upper_score = livsmedelsverket.advanced_fuzzy_match(
        "PANNKAKA", "Pannkaka tunn hemlagad"
    )
    lower_score = livsmedelsverket.advanced_fuzzy_match(
        "pannkaka", "Pannkaka tunn hemlagad"
    )
    assert upper_score == lower_score


def test_acceptable_performance_for_advanced_fuzzy_match():
    start = time.perf_counter_ns()
    livsmedelsverket.advanced_fuzzy_match("pannkaka", "Pannkaka tunn hemlagad", None)
    end = time.perf_counter_ns()
    match_time = end - start
    print(
        f"\n"
        f"-------------------------------------------------------------------------------\n"
        f"Advanced fuzzy match took {match_time / 1000} microseconds \n"
        f"-------------------------------------------------------------------------------"
    )
    # Less than 20 microseconds per match
    assert match_time <= 20 * 10**3


def test_acceptable_performance_for_livsmedelsverket_search():
    client = livsmedelsverket.LivsmedelsverketClient()
    start = time.perf_counter_ns()
    client.search_foods_by_name("pannkaka")
    end = time.perf_counter_ns()
    search_time = end - start
    print(
        f"\n"
        f"-------------------------------------------------------------------------------\n"
        f"DB search took {search_time / 1_000_000} milliseconds \n"
        f"-------------------------------------------------------------------------------"
    )
    # Less than 150 milliseconds for a search
    assert search_time <= 150 * 10**6


def test_ingredient_object_from_livsmedelsverket():
    client = livsmedelsverket.LivsmedelsverketClient()

    # Simple values
    ing = client.get_food_by_id(0)
    assert ing.id == 0
    assert ing.name == "Nöt talg"
    assert ing.protein == 0.0
    assert ing.fat == 100.0
    assert ing.carbs == 0.0
    assert ing.calories == 884
    assert ing.food_number == 1

    # Diverse values
    ing = client.get_food_by_id(33)
    assert ing.id == 33
    assert ing.name == "Räkmajonnäs räksallad gatukök"
    assert ing.protein == 5.2
    assert ing.fat == 48.0
    assert ing.carbs == 2.9
    assert ing.calories == 457
    assert ing.food_number == 52
