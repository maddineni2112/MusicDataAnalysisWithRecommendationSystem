from __future__ import annotations

from app.services.labeling import LANGUAGE_KEYWORDS, MOOD_KEYWORDS, TYPE_KEYWORDS


ERA_PATTERNS = {
    "1990s": (1990, 1999),
    "2000s": (2000, 2009),
    "2010s": (2010, 2019),
    "2020s": (2020, 2029),
    "old": (1900, 1999),
    "classic": (1900, 2009),
    "new": (2020, 2030),
    "latest": (2020, 2030),
    "recent": (2020, 2030),
}


def parse_recommendation_query(query: str | None) -> dict:
    if not query:
        return {}
    text = query.lower()
    filters: dict[str, str | int] = {}
    _match_keyword_dimension(text, filters, "language", LANGUAGE_KEYWORDS)
    _match_keyword_dimension(text, filters, "mood", MOOD_KEYWORDS)
    _match_keyword_dimension(text, filters, "music_type", TYPE_KEYWORDS)
    for token, (min_year, max_year) in ERA_PATTERNS.items():
        if token in text:
            filters["min_year"] = min_year
            filters["max_year"] = max_year
            break
    return filters


def _match_keyword_dimension(text: str, filters: dict, dimension: str, keyword_map: dict[str, list[str]]) -> None:
    for value, keywords in keyword_map.items():
        if value.lower() in text or any(keyword in text for keyword in keywords):
            filters[dimension] = value
            return
