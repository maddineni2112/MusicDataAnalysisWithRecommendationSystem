from __future__ import annotations

from dataclasses import dataclass


LANGUAGE_KEYWORDS = {
    "Hindi": ["hindi", "bollywood"],
    "Telugu": ["telugu", "tollywood"],
    "Tamil": ["tamil", "kollywood"],
    "Malayalam": ["malayalam", "mollywood"],
    "Kannada": ["kannada", "sandalwood"],
    "Punjabi": ["punjabi"],
    "Bengali": ["bengali", "bangla"],
    "Marathi": ["marathi"],
}

TYPE_KEYWORDS = {
    "film": ["bollywood", "tollywood", "kollywood", "film", "movie", "soundtrack"],
    "indie": ["indie", "independent"],
    "devotional": ["devotional", "bhakti", "spiritual", "aarti", "mantra"],
    "classical": ["classical", "carnatic", "hindustani"],
    "folk": ["folk", "traditional"],
    "pop": ["pop"],
    "rap_hiphop": ["rap", "hip hop", "hip-hop"],
}

MOOD_KEYWORDS = {
    "sad": ["sad", "breakup", "heartbreak", "melancholy"],
    "romantic": ["romantic", "love", "romance"],
    "energetic": ["party", "dance", "workout", "energetic", "beats"],
    "devotional": ["devotional", "bhakti", "spiritual"],
    "calm": ["calm", "soothing", "chill", "lofi"],
}


@dataclass(frozen=True)
class InferredLabelData:
    dimension: str
    value: str
    confidence: float
    evidence: dict


def infer_labels(*, track_name: str, album_name: str | None, artist_names: list[str], source_text: str = "") -> list[InferredLabelData]:
    text = " ".join([track_name or "", album_name or "", " ".join(artist_names), source_text or ""]).lower()
    labels: list[InferredLabelData] = []
    labels.extend(_infer_dimension("language", LANGUAGE_KEYWORDS, text))
    labels.extend(_infer_dimension("music_type", TYPE_KEYWORDS, text))
    labels.extend(_infer_dimension("mood", MOOD_KEYWORDS, text))
    if not any(label.dimension == "region" for label in labels):
        labels.append(InferredLabelData("region", "India", 0.55, {"rule": "project_scope_default"}))
    return labels


def _infer_dimension(dimension: str, keyword_map: dict[str, list[str]], text: str) -> list[InferredLabelData]:
    matches = []
    for value, keywords in keyword_map.items():
        hit_keywords = [keyword for keyword in keywords if keyword in text]
        if hit_keywords:
            confidence = min(0.95, 0.6 + (len(hit_keywords) * 0.1))
            matches.append(InferredLabelData(dimension, value, confidence, {"keywords": hit_keywords}))
    return matches
