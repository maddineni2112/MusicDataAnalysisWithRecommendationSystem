from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.entities import Artist, DataQualityResult, InferredLabel, ModelRun, Playlist, PlaylistTrack, Track, TrackArtist
from app.schemas.entities import ArtistOut, DashboardOverview, PaginatedPlaylists, PaginatedTracks, TrackOut
from app.services.dashboard import analytics_summary, language_trends, overview
from app.services.labels import effective_labels_for_track, label_overrides_for_track
from app.services.nl_query import parse_recommendation_query
from app.services.quality import quality_summary
from app.services.recommender import recommend_tracks

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "indian-music-intelligence-api"}


@router.get("/tracks", response_model=PaginatedTracks)
def list_tracks(
    q: str | None = None,
    language: str | None = None,
    mood: str | None = None,
    music_type: str | None = None,
    limit: int = Query(25, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    stmt = select(Track).options(selectinload(Track.labels)).order_by(Track.name).limit(limit).offset(offset)
    count_stmt = select(func.count()).select_from(Track)
    if q:
        stmt = stmt.where(Track.name.ilike(f"%{q}%"))
        count_stmt = count_stmt.where(Track.name.ilike(f"%{q}%"))
    label_filters = {"language": language, "mood": mood, "music_type": music_type}
    for dimension, value in ((key, value) for key, value in label_filters.items() if value):
        stmt = stmt.where(Track.id.in_(select(InferredLabel.track_id).where(InferredLabel.dimension == dimension, InferredLabel.value == value)))
        count_stmt = count_stmt.where(Track.id.in_(select(InferredLabel.track_id).where(InferredLabel.dimension == dimension, InferredLabel.value == value)))
    return {"total": db.scalar(count_stmt) or 0, "limit": limit, "offset": offset, "items": db.scalars(stmt).all()}


@router.get("/tracks/{track_id}", response_model=TrackOut)
def get_track(track_id: int, db: Session = Depends(get_db)) -> Track:
    track = db.scalars(select(Track).options(selectinload(Track.labels)).where(Track.id == track_id)).first()
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


@router.get("/tracks/{track_id}/detail")
def get_track_detail(track_id: int, db: Session = Depends(get_db)) -> dict:
    track = db.scalars(select(Track).options(selectinload(Track.labels)).where(Track.id == track_id)).first()
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")
    artists = db.execute(
        select(Artist.id, Artist.name, Artist.spotify_url)
        .join(TrackArtist, TrackArtist.artist_id == Artist.id)
        .where(TrackArtist.track_id == track_id)
        .order_by(Artist.name)
    ).mappings().all()
    playlists = db.execute(
        select(Playlist.id, Playlist.name, Playlist.source_category, Playlist.source_url)
        .join(PlaylistTrack, PlaylistTrack.playlist_id == Playlist.id)
        .where(PlaylistTrack.track_id == track_id)
        .order_by(Playlist.name)
        .limit(25)
    ).mappings().all()
    recommendations = recommend_tracks(db, track_id, limit=5)
    return {
        "track": TrackOut.model_validate(track),
        "effective_labels": effective_labels_for_track(db, track_id),
        "label_overrides": label_overrides_for_track(db, track_id),
        "artists": [dict(row) for row in artists],
        "playlists": [dict(row) for row in playlists],
        "similar_tracks": [
            {
                "track": TrackOut.model_validate(item["track"]),
                "score": item["score"],
                "reasons": item["reasons"],
                "score_breakdown": item["score_breakdown"],
            }
            for item in recommendations
        ],
    }


@router.get("/artists", response_model=list[ArtistOut])
def list_artists(q: str | None = None, limit: int = Query(25, le=100), db: Session = Depends(get_db)) -> list[Artist]:
    stmt = select(Artist).order_by(Artist.name).limit(limit)
    if q:
        stmt = stmt.where(Artist.name.ilike(f"%{q}%"))
    return list(db.scalars(stmt).all())


@router.get("/artists/{artist_id}", response_model=ArtistOut)
def get_artist(artist_id: int, db: Session = Depends(get_db)) -> Artist:
    artist = db.get(Artist, artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.get("/artists/{artist_id}/detail")
def get_artist_detail(artist_id: int, db: Session = Depends(get_db)) -> dict:
    artist = db.get(Artist, artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    tracks = db.scalars(
        select(Track)
        .join(TrackArtist, TrackArtist.track_id == Track.id)
        .options(selectinload(Track.labels))
        .where(TrackArtist.artist_id == artist_id)
        .order_by(Track.popularity.desc().nullslast(), Track.name)
        .limit(20)
    ).all()
    label_rows = db.execute(
        select(InferredLabel.dimension, InferredLabel.value, func.count())
        .join(TrackArtist, TrackArtist.track_id == InferredLabel.track_id)
        .where(TrackArtist.artist_id == artist_id)
        .group_by(InferredLabel.dimension, InferredLabel.value)
        .order_by(InferredLabel.dimension, func.count().desc())
    ).all()
    collaborators = db.execute(
        select(Artist.id, Artist.name, func.count())
        .join(TrackArtist, TrackArtist.artist_id == Artist.id)
        .where(
            TrackArtist.track_id.in_(select(TrackArtist.track_id).where(TrackArtist.artist_id == artist_id)),
            Artist.id != artist_id,
        )
        .group_by(Artist.id, Artist.name)
        .order_by(func.count().desc(), Artist.name)
        .limit(10)
    ).all()
    return {
        "artist": ArtistOut.model_validate(artist),
        "tracks": [TrackOut.model_validate(track) for track in tracks],
        "label_mix": [{"dimension": dimension, "value": value, "count": count} for dimension, value, count in label_rows],
        "collaborators": [{"id": row[0], "name": row[1], "shared_tracks": row[2]} for row in collaborators],
    }


@router.get("/artist-network")
def artist_network(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(TrackArtist.track_id, Artist.id, Artist.name)
        .join(Artist, Artist.id == TrackArtist.artist_id)
        .order_by(TrackArtist.track_id, Artist.name)
    ).all()
    nodes: dict[int, dict] = {}
    edge_counts: dict[tuple[int, int], int] = {}
    artists_by_track: dict[int, list[tuple[int, str]]] = {}
    for track_id, artist_id, name in rows:
        nodes[artist_id] = {"id": artist_id, "name": name}
        artists_by_track.setdefault(track_id, []).append((artist_id, name))
    for artists in artists_by_track.values():
        for index, source in enumerate(artists):
            for target in artists[index + 1 :]:
                key = tuple(sorted((source[0], target[0])))
                edge_counts[key] = edge_counts.get(key, 0) + 1
    edges = [
        {"source": source, "target": target, "weight": weight}
        for (source, target), weight in sorted(edge_counts.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]
    connected_ids = {edge["source"] for edge in edges} | {edge["target"] for edge in edges}
    return {
        "nodes": [node for artist_id, node in nodes.items() if artist_id in connected_ids] or list(nodes.values())[:limit],
        "edges": edges,
        "track_count": len(artists_by_track),
    }


@router.get("/playlists", response_model=PaginatedPlaylists)
def list_playlists(limit: int = Query(25, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)) -> dict:
    stmt = select(Playlist).order_by(Playlist.name).limit(limit).offset(offset)
    return {"total": db.scalar(select(func.count()).select_from(Playlist)) or 0, "limit": limit, "offset": offset, "items": db.scalars(stmt).all()}


@router.get("/dashboard/overview", response_model=DashboardOverview)
def dashboard_overview(db: Session = Depends(get_db)) -> dict:
    return overview(db)


@router.get("/dashboard/trends")
def dashboard_trends(db: Session = Depends(get_db)) -> dict:
    return {"language_trends": language_trends(db)}


@router.get("/dashboard/analytics")
def dashboard_analytics(db: Session = Depends(get_db)) -> dict:
    return analytics_summary(db)


@router.get("/recommendations")
def recommendations(
    track_id: int,
    limit: int = Query(10, ge=1, le=50),
    language: str | None = None,
    mood: str | None = None,
    music_type: str | None = None,
    query: str | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    db: Session = Depends(get_db),
) -> dict:
    filters = {"language": language, "mood": mood, "music_type": music_type}
    filters.update(parse_recommendation_query(query))
    if min_year is not None:
        filters["min_year"] = min_year
    if max_year is not None:
        filters["max_year"] = max_year
    filters = {key: value for key, value in filters.items() if value}
    results = recommend_tracks(db, track_id, limit=limit, filters=filters)
    return {
        "seed_track_id": track_id,
        "limit": limit,
        "items": [
            {
                "track": TrackOut.model_validate(item["track"]),
                "score": item["score"],
                "reasons": item["reasons"],
                "score_breakdown": item["score_breakdown"],
            }
            for item in results
        ],
        "parsed_query_filters": parse_recommendation_query(query),
    }


@router.get("/model-insights")
def model_insights(db: Session = Depends(get_db)) -> dict:
    track_count = db.scalar(select(func.count()).select_from(Track)) or 0
    label_count = db.scalar(select(func.count()).select_from(InferredLabel)) or 0
    latest_quality = db.scalar(select(func.max(DataQualityResult.created_at)))
    latest_model = db.scalars(select(ModelRun).order_by(ModelRun.created_at.desc()).limit(1)).first()
    return {
        "recommender": "hybrid_metadata_playlist_text",
        "default_result_count": 10,
        "evaluation_plan": "playlist holdout evaluation with coverage, diversity, novelty, and seed-exclusion checks",
        "signals": ["language", "mood", "music_type", "region", "release era", "official popularity"],
        "natural_language_parser": "rule-based filters for language, mood, type, and era",
        "dataset": {
            "tracks": track_count,
            "labels": label_count,
            "label_density": round(label_count / track_count, 2) if track_count else 0,
            "latest_quality_run": latest_quality.isoformat() if latest_quality else None,
        },
        "latest_model_run": {
            "id": latest_model.id,
            "model_type": latest_model.model_type,
            "version": latest_model.version,
            "metrics": latest_model.metrics,
            "artifact_path": latest_model.artifact_path,
        }
        if latest_model
        else None,
        "deferrals": ["paid LLM APIs", "audio playback", "public accounts"],
    }


@router.get("/data-quality/summary")
def data_quality_summary(db: Session = Depends(get_db)) -> dict:
    return quality_summary(db)
