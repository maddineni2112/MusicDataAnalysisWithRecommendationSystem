"""Reusable helpers for content-based music recommendations.

The notebook contains the full exploratory workflow. This module keeps the
recommendation idea in a smaller, reusable form for portfolio review.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pyspark.ml import Pipeline
from pyspark.ml.feature import PCA, StandardScaler, VectorAssembler
from pyspark.sql import DataFrame
from pyspark.sql import functions as fn
from pyspark.sql.types import FloatType


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


def build_pca_pipeline(k: int = 10, input_cols: list[str] | None = None) -> Pipeline:
    """Create a Spark ML pipeline that converts song features into PCA vectors."""

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


def recommend_similar_songs(
    music_pca_df: DataFrame,
    song_name: str,
    limit: int = 5,
) -> pd.DataFrame:
    """Return songs nearest to the requested song in PCA feature space.

    Parameters
    ----------
    music_pca_df:
        Spark DataFrame containing `name`, `artists`, and `pca_score` columns.
    song_name:
        Track name to use as the recommendation seed.
    limit:
        Number of recommendations to return.
    """

    distance_udf = fn.udf(l2_distance, FloatType())

    recommendations = (
        music_pca_df.where(fn.col("name") == song_name)
        .select(fn.col("pca_score").alias("seed_score"))
        .join(music_pca_df)
        .withColumn("distance", distance_udf("pca_score", "seed_score"))
        .where(fn.col("distance") != 0)
        .orderBy(fn.asc("distance"))
        .select("name", "artists", "distance")
        .limit(limit)
    )

    return recommendations.toPandas()
