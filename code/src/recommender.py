"""Reusable helpers for content-based music recommendations.

The notebook contains the full exploratory workflow. This module keeps the
recommendation idea in a smaller, reusable form for portfolio review.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


AUDIO_FEATURES = [
    "acousticness",
    "danceability",
    "energy",
    "explicit",
    "instrumentalness",
    "key",
    "liveness",
    "loudness",
    "mode",
    "speechiness",
    "tempo",
    "valence",
    "year",
]


SparkOrPandasDataFrame = Any | pd.DataFrame


def _spark_imports():
    try:
        from pyspark.ml import Pipeline
        from pyspark.ml.feature import PCA, StandardScaler, VectorAssembler
        from pyspark.sql import functions as fn
        from pyspark.sql.types import FloatType
    except ImportError as exc:
        raise ImportError("PySpark is required for Spark DataFrame recommendations.") from exc

    return Pipeline, PCA, StandardScaler, VectorAssembler, fn, FloatType


def _small_to_pandas(df: SparkOrPandasDataFrame) -> pd.DataFrame:
    """Convert a small Spark result to Pandas without relying on Spark's toPandas."""

    if isinstance(df, pd.DataFrame):
        return df.copy()
    rows = [row.asDict(recursive=True) for row in df.collect()]
    return pd.DataFrame(rows, columns=df.columns)


def _find_seed_tracks_pandas(
    music_pca_df: pd.DataFrame,
    *,
    track_id: str | None = None,
    song_name: str | None = None,
    artist_name: str | None = None,
    limit: int = 10,
) -> pd.DataFrame:
    query = music_pca_df
    if track_id is not None and "id" in query.columns:
        query = query[query["id"] == track_id]
    if song_name is not None:
        query = query[query["name"].str.lower() == song_name.lower()]
    if artist_name is not None:
        query = query[query["artists"].str.lower().str.contains(artist_name.lower(), regex=False)]

    candidate_cols = [col for col in ["id", "name", "artists", "popularity", "year"] if col in query.columns]
    return query.loc[:, candidate_cols].head(limit).reset_index(drop=True)


def build_pca_pipeline(k: int = 10, input_cols: list[str] | None = None) -> Pipeline:
    """Create a Spark ML pipeline that converts song features into PCA vectors."""

    Pipeline, PCA, StandardScaler, VectorAssembler, _, _ = _spark_imports()

    features = input_cols or AUDIO_FEATURES
    return Pipeline(
        stages=[
            VectorAssembler(inputCols=features, outputCol="features"),
            StandardScaler(
                withMean=True,
                withStd=True,
                inputCol="features",
                outputCol="scaled_features",
            ),
            PCA(k=k, inputCol="scaled_features", outputCol="pca_score"),
        ]
    )


def l2_distance(left: np.ndarray, right: np.ndarray) -> float:
    """Return Euclidean distance between two vectors."""

    left = np.asarray(left)
    right = np.asarray(right)
    return float(np.sqrt((left - right).T.dot(left - right)))


def find_seed_tracks(
    music_pca_df: SparkOrPandasDataFrame,
    *,
    track_id: str | None = None,
    song_name: str | None = None,
    artist_name: str | None = None,
    limit: int = 10,
) -> pd.DataFrame:
    """Find candidate seed tracks for a recommendation request.

    Provide `track_id` for an exact lookup, or use `song_name` with optional
    `artist_name` when the track id is not known.
    """

    if not any([track_id, song_name, artist_name]):
        raise ValueError("Provide track_id, song_name, or artist_name.")

    if isinstance(music_pca_df, pd.DataFrame):
        return _find_seed_tracks_pandas(
            music_pca_df,
            track_id=track_id,
            song_name=song_name,
            artist_name=artist_name,
            limit=limit,
        )

    _, _, _, _, fn, _ = _spark_imports()
    query = music_pca_df
    if track_id is not None and "id" in music_pca_df.columns:
        query = query.where(fn.col("id") == track_id)
    if song_name is not None:
        query = query.where(fn.lower(fn.col("name")) == song_name.lower())
    if artist_name is not None:
        query = query.where(fn.lower(fn.col("artists")).contains(artist_name.lower()))

    candidate_cols = [col for col in ["id", "name", "artists", "popularity", "year"] if col in query.columns]
    return _small_to_pandas(query.select(*candidate_cols).limit(limit))


def recommend_similar_songs(
    music_pca_df: SparkOrPandasDataFrame,
    song_name: str | None = None,
    *,
    track_id: str | None = None,
    artist_name: str | None = None,
    limit: int = 5,
) -> pd.DataFrame:
    """Return songs nearest to the requested song in PCA feature space.

    Parameters
    ----------
    music_pca_df:
        Spark DataFrame containing track metadata and a `pca_score` column.
    song_name:
        Track name to use as the recommendation seed.
    track_id:
        Spotify track id to use for an exact seed lookup.
    artist_name:
        Artist name to disambiguate a track-name search.
    limit:
        Number of recommendations to return.
    """

    candidates = find_seed_tracks(
        music_pca_df,
        track_id=track_id,
        song_name=song_name,
        artist_name=artist_name,
        limit=limit + 1,
    )

    if candidates.empty:
        return pd.DataFrame(
            [{"status": "not_found", "message": "No matching song was found. Try track_id, song_name, or artist_name."}]
        )
    if len(candidates) > 1:
        candidates = candidates.copy()
        candidates.insert(0, "status", "ambiguous")
        return candidates

    seed = candidates.iloc[0]
    if isinstance(music_pca_df, pd.DataFrame):
        seed_id = seed["id"] if "id" in candidates.columns else None
        seed_score = music_pca_df.loc[music_pca_df["id"] == seed_id, "pca_score"].iloc[0]
        recommendations = music_pca_df.copy()
        if seed_id is not None and "id" in recommendations.columns:
            recommendations = recommendations[recommendations["id"] != seed_id]
        recommendations["distance"] = recommendations["pca_score"].apply(lambda score: l2_distance(score, seed_score))
        output_cols = [col for col in ["id", "name", "artists", "popularity", "year", "distance"] if col in recommendations.columns]
        result = recommendations.sort_values("distance").loc[:, output_cols].head(limit).reset_index(drop=True)
        result.insert(0, "status", "ok")
        return result

    _, _, _, _, fn, FloatType = _spark_imports()
    distance_udf = fn.udf(l2_distance, FloatType())
    seed_filter = fn.lit(True)
    if track_id is not None and "id" in music_pca_df.columns:
        seed_filter = fn.col("id") == track_id
    elif "id" in music_pca_df.columns and "id" in candidates.columns:
        seed_filter = fn.col("id") == seed["id"]
    elif song_name is not None:
        seed_filter = fn.col("name") == song_name

    recommendations = (
        music_pca_df.where(seed_filter)
        .select(fn.col("pca_score").alias("seed_score"))
        .join(music_pca_df)
        .withColumn("distance", distance_udf("pca_score", "seed_score"))
        .where(fn.col("distance") > 0)
        .orderBy(fn.asc("distance"))
        .limit(limit)
    )
    output_cols = [col for col in ["id", "name", "artists", "popularity", "year", "distance"] if col in recommendations.columns]
    result = _small_to_pandas(recommendations.select(*output_cols))
    result.insert(0, "status", "ok")

    return result
