from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.entities import Artist, InferredLabel, Playlist, Track
from app.schemas.entities import ArtistOut, DashboardOverview, PaginatedPlaylists, PaginatedTracks, TrackOut
from app.services.dashboard import language_trends, overview
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
def model_insights() -> dict:
    return {
        "recommender": "hybrid_metadata_playlist_text",
        "default_result_count": 10,
        "evaluation_plan": "playlist holdout evaluation",
        "signals": ["language", "mood", "music_type", "region", "release era", "official popularity"],
        "natural_language_parser": "rule-based filters for language, mood, type, and era",
        "deferrals": ["paid LLM APIs", "audio playback", "public accounts"],
    }


@router.get("/data-quality/summary")
def data_quality_summary(db: Session = Depends(get_db)) -> dict:
    return quality_summary(db)
