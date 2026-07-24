from app.services.nl_query import parse_recommendation_query


def test_parse_telugu_romantic_2010s_query() -> None:
    filters = parse_recommendation_query("romantic Telugu songs from the 2010s")
    assert filters["language"] == "Telugu"
    assert filters["mood"] == "romantic"
    assert filters["min_year"] == 2010
    assert filters["max_year"] == 2019
