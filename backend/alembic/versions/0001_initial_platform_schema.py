"""Initial Indian Music Intelligence Platform schema."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_platform_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tracks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=120), unique=True, index=True),
        sa.Column("name", sa.String(length=320), nullable=False, index=True),
        sa.Column("album_name", sa.String(length=320), index=True),
        sa.Column("release_date", sa.String(length=40), index=True),
        sa.Column("release_year", sa.Integer(), index=True),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("popularity", sa.Integer(), index=True),
        sa.Column("explicit", sa.Boolean(), default=False),
        sa.Column("spotify_url", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "artists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=120), unique=True, index=True),
        sa.Column("name", sa.String(length=260), nullable=False, index=True),
        sa.Column("genres", sa.JSON(), default=list),
        sa.Column("spotify_url", sa.String(length=500)),
    )
    op.create_table(
        "playlists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=120), unique=True, index=True),
        sa.Column("name", sa.String(length=320), nullable=False, index=True),
        sa.Column("description", sa.Text()),
        sa.Column("source_category", sa.String(length=120), index=True),
        sa.Column("source_url", sa.String(length=500)),
    )
    op.create_table(
        "track_artists",
        sa.Column("track_id", sa.ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("artist_id", sa.ForeignKey("artists.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "playlist_tracks",
        sa.Column("playlist_id", sa.ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("track_id", sa.ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("position", sa.Integer()),
    )
    op.create_table(
        "collection_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=220), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False, index=True),
        sa.Column("license", sa.String(length=260)),
        sa.Column("citation", sa.Text()),
        sa.Column("url", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "raw_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.ForeignKey("collection_sources.id", ondelete="SET NULL")),
        sa.Column("record_type", sa.String(length=80), index=True),
        sa.Column("external_id", sa.String(length=120), index=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "inferred_labels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("track_id", sa.ForeignKey("tracks.id", ondelete="CASCADE"), index=True),
        sa.Column("dimension", sa.String(length=80), index=True),
        sa.Column("value", sa.String(length=120), index=True),
        sa.Column("confidence", sa.Float(), default=0.0),
        sa.Column("evidence", sa.JSON(), default=dict),
    )
    op.create_table(
        "label_overrides",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("track_id", sa.ForeignKey("tracks.id", ondelete="CASCADE"), index=True),
        sa.Column("dimension", sa.String(length=80), index=True),
        sa.Column("value", sa.String(length=120)),
        sa.Column("reason", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "track_features",
        sa.Column("track_id", sa.ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("feature_text", sa.Text()),
        sa.Column("feature_payload", sa.JSON(), default=dict),
    )
    op.create_table(
        "job_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_type", sa.String(length=120), index=True),
        sa.Column("status", sa.String(length=40), index=True),
        sa.Column("parameters", sa.JSON(), default=dict),
        sa.Column("rows_read", sa.Integer(), default=0),
        sa.Column("rows_written", sa.Integer(), default=0),
        sa.Column("rows_skipped", sa.Integer(), default=0),
        sa.Column("failure_count", sa.Integer(), default=0),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "job_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.ForeignKey("job_runs.id", ondelete="CASCADE"), index=True),
        sa.Column("level", sa.String(length=40), default="info"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), default=dict),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "model_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_type", sa.String(length=120), index=True),
        sa.Column("version", sa.String(length=80), index=True),
        sa.Column("metrics", sa.JSON(), default=dict),
        sa.Column("artifact_path", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "recommendation_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("seed_track_id", sa.ForeignKey("tracks.id", ondelete="SET NULL")),
        sa.Column("model_run_id", sa.ForeignKey("model_runs.id", ondelete="SET NULL")),
        sa.Column("parameters", sa.JSON(), default=dict),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "recommendation_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.ForeignKey("recommendation_runs.id", ondelete="CASCADE"), index=True),
        sa.Column("track_id", sa.ForeignKey("tracks.id", ondelete="CASCADE")),
        sa.Column("rank", sa.Integer()),
        sa.Column("score", sa.Float()),
        sa.Column("reasons", sa.JSON(), default=list),
        sa.Column("score_breakdown", sa.JSON(), default=dict),
    )
    op.create_table(
        "dashboard_cache",
        sa.Column("cache_key", sa.String(length=180), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "data_quality_checks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), unique=True),
        sa.Column("description", sa.Text()),
        sa.Column("severity", sa.String(length=40), default="warning"),
    )
    op.create_table(
        "data_quality_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("check_id", sa.ForeignKey("data_quality_checks.id", ondelete="CASCADE")),
        sa.Column("status", sa.String(length=40), index=True),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column("sample", sa.JSON(), default=list),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in [
        "data_quality_results",
        "data_quality_checks",
        "dashboard_cache",
        "recommendation_results",
        "recommendation_runs",
        "model_runs",
        "job_events",
        "job_runs",
        "track_features",
        "label_overrides",
        "inferred_labels",
        "raw_snapshots",
        "collection_sources",
        "playlist_tracks",
        "track_artists",
        "playlists",
        "artists",
        "tracks",
    ]:
        op.drop_table(table)
