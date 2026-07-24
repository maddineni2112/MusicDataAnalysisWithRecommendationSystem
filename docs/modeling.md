# Modeling

The v2 recommender starts with a hybrid scoring scaffold:

- language similarity
- mood similarity
- music type similarity
- region similarity
- release-era closeness
- official popularity proximity when available
- diversity penalty

Planned improvements:

- TF-IDF text similarity
- sentence embeddings when feasible
- playlist co-occurrence features
- pgvector similarity when hosting supports it
- playlist holdout evaluation
- popularity prediction as a secondary demo when official popularity exists

## Label Overrides

Automatic labels remain the default source of truth for scale. Owner/admin overrides are stored separately in `label_overrides`, replacing the effective value for a dimension without deleting inferred label evidence. Recommender filters and scoring use effective labels so owner corrections are reflected in demo behavior.
