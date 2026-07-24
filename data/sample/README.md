# Sample Data

`indian_music_sample.csv` is a tiny sanitized dataset for local smoke tests and screenshots. Large public datasets, Spotify exports, raw snapshots, model artifacts, and vector indexes must stay out of Git.

`public_playlist_sample.json` mimics public playlist datasets such as Spotify Million Playlist Dataset-style JSON. It is intentionally tiny and safe to commit, but exercises playlist lineage, repeated artists, and co-occurrence import paths.

The scalable acquisition plan is tracked separately in `data/seeds/indian_music_seed_manifest.json`. Use `python -m app.cli seeds validate` and `python -m app.cli seeds export` to prepare reviewed Spotify/public dataset seed files under ignored `data/raw/`.
