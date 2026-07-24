from app.services.labeling import infer_labels


def test_infer_telugu_romantic_film_labels() -> None:
    labels = infer_labels(
        track_name="Romantic Telugu Melody",
        album_name="Tollywood Love Hits",
        artist_names=["Sample Artist"],
        source_text="Telugu romantic film playlist",
    )
    pairs = {(label.dimension, label.value) for label in labels}
    assert ("language", "Telugu") in pairs
    assert ("mood", "romantic") in pairs
    assert ("music_type", "film") in pairs
