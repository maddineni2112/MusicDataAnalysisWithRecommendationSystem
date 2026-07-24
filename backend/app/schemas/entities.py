from pydantic import BaseModel, ConfigDict


class LabelOut(BaseModel):
    dimension: str
    value: str
    confidence: float
    evidence: dict

    model_config = ConfigDict(from_attributes=True)


class TrackOut(BaseModel):
    id: int
    external_id: str | None
    name: str
    album_name: str | None
    release_date: str | None
    release_year: int | None
    duration_ms: int | None
    popularity: int | None
    explicit: bool
    spotify_url: str | None
    labels: list[LabelOut] = []

    model_config = ConfigDict(from_attributes=True)


class ArtistOut(BaseModel):
    id: int
    external_id: str | None
    name: str
    genres: list
    spotify_url: str | None

    model_config = ConfigDict(from_attributes=True)


class PaginatedTracks(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TrackOut]


class RecommendationOut(BaseModel):
    track: TrackOut
    score: float
    reasons: list[str]
    score_breakdown: dict


class DashboardOverview(BaseModel):
    tracks: int
    artists: int
    playlists: int
    languages: int
    label_confidence_avg: float | None
    official_popularity_available: int
