import pytest

from app.services.seed_manifest import (
    playlist_ids_from_manifest,
    search_queries_from_manifest,
    summarize_seed_manifest,
    validate_seed_manifest,
    write_playlist_id_file,
    write_search_query_file,
)


def sample_manifest() -> dict:
    return {
        "name": "Test Seeds",
        "version": "v2-test",
        "market": "IN",
        "language_groups": [
            {
                "language": "Telugu",
                "categories": ["film", "indie"],
                "spotify_search_queries": ["Telugu film hits", "Telugu indie"],
                "playlist_ids": ["abc", "def", "abc"],
            },
            {
                "language": "Hindi",
                "categories": ["film"],
                "spotify_search_queries": ["Hindi film hits"],
                "playlist_ids": [],
            },
        ],
    }


def test_seed_manifest_summary_and_deduped_playlist_ids() -> None:
    manifest = sample_manifest()
    summary = summarize_seed_manifest(manifest)

    assert summary["language_count"] == 2
    assert summary["search_query_count"] == 3
    assert summary["playlist_id_count"] == 2
    assert playlist_ids_from_manifest(manifest) == ["abc", "def"]
    assert search_queries_from_manifest(manifest)[0] == {"language": "Telugu", "query": "Telugu film hits"}


def test_seed_manifest_validation_rejects_missing_queries() -> None:
    manifest = sample_manifest()
    manifest["language_groups"][0]["spotify_search_queries"] = []

    with pytest.raises(ValueError, match="spotify_search_queries"):
        validate_seed_manifest(manifest)


def test_seed_manifest_writers(tmp_path) -> None:
    manifest = sample_manifest()
    playlist_path = tmp_path / "playlist_ids.txt"
    query_path = tmp_path / "queries.csv"

    assert write_playlist_id_file(manifest, playlist_path) == 2
    assert write_search_query_file(manifest, query_path) == 3
    assert playlist_path.read_text(encoding="utf-8").splitlines() == ["abc", "def"]
    assert "language,query" in query_path.read_text(encoding="utf-8")
