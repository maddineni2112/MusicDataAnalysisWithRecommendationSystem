from types import SimpleNamespace

from sklearn.feature_extraction.text import TfidfVectorizer

from app.services.features import tfidf_similarity_scores
from app.services.recommender import DEFAULT_WEIGHTS, score_candidate


def test_default_weights_are_configured_for_balanced_discovery() -> None:
    assert DEFAULT_WEIGHTS["language"] > DEFAULT_WEIGHTS["popularity"]
    assert "mood" in DEFAULT_WEIGHTS
    assert DEFAULT_WEIGHTS["text_similarity"] > DEFAULT_WEIGHTS["era"]


def test_tfidf_similarity_scores_from_artifact() -> None:
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(["telugu romantic melody", "telugu love melody", "punjabi dance pop"])
    scores = tfidf_similarity_scores(
        1,
        [2, 3],
        {
            "kind": "tfidf_track_index",
            "version": "test",
            "track_ids": [1, 2, 3],
            "vectorizer": vectorizer,
            "matrix": matrix,
        },
    )

    assert scores[2] > scores[3]
    assert scores[2] > 0


def test_score_candidate_includes_text_similarity_breakdown() -> None:
    seed = SimpleNamespace(release_year=2015, popularity=70)
    candidate = SimpleNamespace(release_year=2016, popularity=68)
    score, reasons, breakdown = score_candidate(
        seed,
        {"language": {"Telugu"}},
        candidate,
        {"language": {"Telugu"}},
        text_similarity=0.5,
    )

    assert score > DEFAULT_WEIGHTS["language"]
    assert breakdown["text_similarity"] == round(DEFAULT_WEIGHTS["text_similarity"] * 0.5, 4)
    assert "strong text similarity" in reasons
