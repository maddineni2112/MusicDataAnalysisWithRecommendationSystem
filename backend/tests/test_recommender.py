from app.services.recommender import DEFAULT_WEIGHTS


def test_default_weights_are_configured_for_balanced_discovery() -> None:
    assert DEFAULT_WEIGHTS["language"] > DEFAULT_WEIGHTS["popularity"]
    assert "mood" in DEFAULT_WEIGHTS
