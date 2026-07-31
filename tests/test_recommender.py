import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code" / "src"))

from recommender import find_seed_tracks, l2_distance, recommend_similar_songs


@pytest.fixture()
def music_pca_df():
    return pd.DataFrame(
        [
            ("track-1", "Echo", "['Artist A']", 70, 2020, [0.0, 0.0]),
            ("track-2", "Echo", "['Artist B']", 65, 2020, [10.0, 10.0]),
            ("track-3", "Near Echo", "['Artist C']", 60, 2020, [0.1, 0.1]),
            ("track-4", "Far Echo", "['Artist D']", 55, 2019, [5.0, 5.0]),
        ],
        columns=["id", "name", "artists", "popularity", "year", "pca_score"],
    )


def test_l2_distance():
    assert l2_distance([0, 0], [3, 4]) == 5.0


def test_find_seed_tracks_by_track_id(music_pca_df):
    result = find_seed_tracks(music_pca_df, track_id="track-1")

    assert len(result) == 1
    assert result.iloc[0]["id"] == "track-1"


def test_recommend_by_song_and_artist(music_pca_df):
    result = recommend_similar_songs(music_pca_df, song_name="Echo", artist_name="Artist A", limit=1)

    assert result.iloc[0]["status"] == "ok"
    assert result.iloc[0]["id"] == "track-3"


def test_ambiguous_song_name_returns_candidates(music_pca_df):
    result = recommend_similar_songs(music_pca_df, song_name="Echo", limit=5)

    assert set(result["status"]) == {"ambiguous"}
    assert set(result["id"]) == {"track-1", "track-2"}


def test_missing_song_returns_clear_result(music_pca_df):
    result = recommend_similar_songs(music_pca_df, song_name="Missing Song", limit=5)

    assert result.iloc[0]["status"] == "not_found"
    assert "No matching song" in result.iloc[0]["message"]
