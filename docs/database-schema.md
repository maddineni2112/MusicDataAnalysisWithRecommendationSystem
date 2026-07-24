# Database Schema

The schema is defined in SQLAlchemy models and Alembic migrations.

Core entities:

- tracks
- artists
- playlists
- track_artists
- playlist_tracks
- collection_sources
- raw_snapshots
- inferred_labels
- label_overrides
- track_features
- job_runs
- job_events
- model_runs
- recommendation_runs
- recommendation_results
- dashboard_cache
- data_quality_checks
- data_quality_results

The design keeps raw source snapshots separate from normalized application tables and preserves source lineage for every imported record.
