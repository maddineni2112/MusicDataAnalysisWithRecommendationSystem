# Data Sources

Primary target sources:

- Spotify playlist-first collection when credentials are available.
- Spotify Million Playlist Dataset-style public playlist data for reproducibility.
- CSV, JSON, and offline SQL dump imports for public datasets.

Source policy:

- Track source name, URL, license, and citation.
- Keep raw snapshots outside normalized tables.
- Keep large raw datasets out of Git.
- Commit only small sanitized sample data.
