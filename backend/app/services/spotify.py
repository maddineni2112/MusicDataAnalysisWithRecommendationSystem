from __future__ import annotations

import base64
import time
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.imports import import_records

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"


def collect_spotify_playlists(
    db: Session,
    *,
    playlist_ids: list[str],
    market: str = "IN",
    limit_per_playlist: int = 100,
    source_name: str = "Spotify playlist collection",
) -> dict:
    settings = get_settings()
    if not settings.spotify_client_id or not settings.spotify_client_secret:
        return {
            "rows_read": 0,
            "rows_written": 0,
            "rows_skipped": len(playlist_ids),
            "failure_count": 0,
            "status": "credential_required",
            "message": "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to enable playlist-first collection.",
        }
    token = fetch_client_credentials_token(settings.spotify_client_id, settings.spotify_client_secret)
    records: list[dict] = []
    for playlist_id in playlist_ids:
        records.extend(fetch_playlist_tracks(token, playlist_id=playlist_id, market=market, limit_per_playlist=limit_per_playlist))
    return import_records(db, records, source_name=source_name, source_type="spotify", source_url="https://developer.spotify.com/documentation/web-api")


def fetch_client_credentials_token(client_id: str, client_secret: str) -> str:
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    response = httpx.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    response.raise_for_status()
    return str(response.json()["access_token"])


def fetch_playlist_tracks(token: str, *, playlist_id: str, market: str, limit_per_playlist: int) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    playlist_response = request_with_rate_limit(f"{SPOTIFY_API_BASE}/playlists/{playlist_id}", headers=headers, params={"market": market})
    playlist = playlist_response.json()
    playlist_name = playlist.get("name") or playlist_id
    playlist_url = (playlist.get("external_urls") or {}).get("spotify")
    playlist_description = playlist.get("description")
    records: list[dict] = []
    url = f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks"
    params: dict[str, object] = {"market": market, "limit": 100, "offset": 0}
    while url and len(records) < limit_per_playlist:
        response = request_with_rate_limit(url, headers=headers, params=params)
        payload = response.json()
        for item in payload.get("items", []):
            track = item.get("track") or {}
            if not track or track.get("is_local"):
                continue
            records.append(normalize_spotify_track(track, playlist_id, playlist_name, playlist_url, playlist_description, item.get("added_at"), len(records) + 1))
            if len(records) >= limit_per_playlist:
                break
        url = payload.get("next")
        params = {}
    return records


def request_with_rate_limit(url: str, *, headers: dict, params: dict | None = None) -> httpx.Response:
    response = httpx.get(url, headers=headers, params=params, timeout=30)
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", "2"))
        time.sleep(retry_after)
        response = httpx.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response


def normalize_spotify_track(
    track: dict,
    playlist_id: str,
    playlist_name: str,
    playlist_url: str | None,
    playlist_description: str | None,
    added_at: str | None,
    position: int,
) -> dict:
    album = track.get("album") or {}
    artists = track.get("artists") or []
    external_urls = track.get("external_urls") or {}
    return {
        "external_id": track.get("id"),
        "name": track.get("name"),
        "artists": ", ".join(artist.get("name", "") for artist in artists if artist.get("name")),
        "album_name": album.get("name"),
        "release_date": album.get("release_date"),
        "release_year": (album.get("release_date") or "")[:4],
        "duration_ms": track.get("duration_ms"),
        "popularity": track.get("popularity"),
        "explicit": track.get("explicit"),
        "spotify_url": external_urls.get("spotify"),
        "playlist_external_id": f"spotify:{playlist_id}",
        "playlist_name": playlist_name,
        "playlist_description": playlist_description,
        "playlist_url": playlist_url,
        "playlist_category": infer_playlist_category(playlist_name),
        "playlist_position": position,
        "source_added_at": added_at,
    }


def infer_playlist_category(name: str) -> str:
    lowered = name.lower()
    for keyword in ["romantic", "love", "party", "dance", "devotional", "bhakti", "classical", "folk", "indie", "rap", "workout", "sad"]:
        if keyword in lowered:
            return keyword
    return "spotify_playlist"


def read_playlist_ids(path: Path | None, playlist_ids: list[str] | None) -> list[str]:
    ids = list(playlist_ids or [])
    if path:
        ids.extend(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#"))
    return list(dict.fromkeys(ids))
