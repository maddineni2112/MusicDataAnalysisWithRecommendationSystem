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

## Supported Local Import Shapes

- CSV tracks: `python -m app.cli import csv data/sample/indian_music_sample.csv --source-name "Sample Indian Music Dataset"`
- Generic JSON tracks: `python -m app.cli import json path/to/tracks.json --source-name "Public Track JSON"`
- Playlist JSON: `python -m app.cli import playlist-json data/sample/public_playlist_sample.json --source-name "Public Playlist Fixture"`

Playlist JSON accepts a top-level `playlists` array. Each playlist can include `pid`, `name`, `description`, `category`, and `tracks`. Each track can include `track_uri`, `track_name`, `artist_name`, `album_name`, `duration_ms`, and `pos`.

## Spotify Collection

Spotify collection uses the Client Credentials flow and does not require public user accounts or saved listener data. It requires:

```text
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
```

Collector example:

```bash
python -m app.cli collect spotify --playlist-id <spotify_playlist_id> --market IN --limit-per-playlist 100
```

For larger seed sets, place one playlist ID per line in a local text file and run:

```bash
python -m app.cli collect spotify --playlist-file data/raw/spotify_playlist_ids.txt --market IN
```

Large seed files and raw exports should stay under ignored folders such as `data/raw/`.

## Indian Music Seed Manifest

The source-controlled acquisition plan lives at:

```text
data/seeds/indian_music_seed_manifest.json
```

It defines the v2 Indian music scope across Hindi, Telugu, Tamil, Malayalam, Kannada, Punjabi, Bengali, and Marathi. Each language group includes regions, categories, Spotify search queries, and an empty `playlist_ids` list for reviewed playlist IDs.

Validate and summarize the manifest:

```bash
python -m app.cli seeds validate
```

Export local acquisition helper files under ignored `data/raw/`:

```bash
python -m app.cli seeds export
```

Credential-gated Spotify collection from reviewed manifest playlist IDs:

```bash
python -m app.cli seeds collect-spotify --limit-per-playlist 100
```

If the manifest has no playlist IDs, the command exits with `needs_playlist_ids` and keeps the search queries as the discovery backlog. This is intentional: it keeps the public repo clean while documenting the scalable collection strategy.
