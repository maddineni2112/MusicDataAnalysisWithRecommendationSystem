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

Planned improvements:

- sentence embeddings when feasible
- playlist co-occurrence features
- pgvector similarity when hosting supports it
- playlist holdout evaluation
- popularity prediction as a secondary demo when official popularity exists

## Label Overrides

Automatic labels remain the default source of truth for scale. Owner/admin overrides are stored separately in `label_overrides`, replacing the effective value for a dimension without deleting inferred label evidence. Recommender filters and scoring use effective labels so owner corrections are reflected in demo behavior.
