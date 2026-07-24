# Modeling

The v2 recommender starts with a hybrid scoring scaffold:

- language similarity
- mood similarity
- music type similarity
- region similarity
- release-era closeness
- official popularity proximity when available
- TF-IDF text similarity from track, artist, playlist, and label text
- diversity penalty

## Feature Build

The local vector-artifact fallback is implemented with scikit-learn TF-IDF:

```bash
docker compose exec api python -m app.cli recommender features
docker compose exec api python -m app.cli recommender rebuild
```

The builder stores feature text in `track_features` and writes an ignored local artifact to `artifacts/recommender/tfidf_index.pkl`. Recommendation scoring loads that artifact when it exists and adds a `text_similarity` score breakdown. If the artifact is missing, the recommender falls back to metadata, labels, era, popularity, and diversity scoring.

## Evaluation

Model evaluation stores `model_runs`, `recommendation_runs`, and `recommendation_results`. Current metrics include:

- coverage
- unique recommended tracks
- average results per seed
- seed-exclusion pass rate
- average score
- playlist holdout hit rate
- playlist holdout average rank
- playlist holdout average candidate count

The holdout check uses playlists with at least two tracks, treats the first playlist track as the seed, holds out the remaining playlist tracks, and measures whether the recommender recovers at least one held-out track in the top results. On the tiny sample dataset this is a smoke/evidence test; on the future 100k-300k track dataset it becomes a stronger recommender quality signal.

Planned improvements:

- sentence embeddings when feasible
- playlist co-occurrence features
- pgvector similarity when hosting supports it
- more robust playlist holdout evaluation on a larger collected dataset
- popularity prediction as a secondary demo when official popularity exists

## Label Overrides

Automatic labels remain the default source of truth for scale. Owner/admin overrides are stored separately in `label_overrides`, replacing the effective value for a dimension without deleting inferred label evidence. Recommender filters and scoring use effective labels so owner corrections are reflected in demo behavior.
