from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_seed_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_seed_manifest(payload)
    return payload


def validate_seed_manifest(payload: dict[str, Any]) -> None:
    required = ["name", "version", "market", "language_groups"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"Seed manifest missing required fields: {', '.join(missing)}")
    groups = payload["language_groups"]
    if not isinstance(groups, list) or not groups:
        raise ValueError("Seed manifest must include at least one language group.")
    seen_languages: set[str] = set()
    for index, group in enumerate(groups, start=1):
        language = group.get("language")
        if not language:
            raise ValueError(f"Language group {index} is missing language.")
        if language in seen_languages:
            raise ValueError(f"Duplicate language group: {language}")
        seen_languages.add(language)
        if not group.get("spotify_search_queries"):
            raise ValueError(f"Language group {language} must include spotify_search_queries.")
        if not isinstance(group.get("playlist_ids", []), list):
            raise ValueError(f"Language group {language} playlist_ids must be a list.")


def summarize_seed_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    groups = payload["language_groups"]
    playlist_ids = playlist_ids_from_manifest(payload)
    search_queries = search_queries_from_manifest(payload)
    categories = sorted({category for group in groups for category in group.get("categories", [])})
    return {
        "name": payload["name"],
        "version": payload["version"],
        "market": payload["market"],
        "language_count": len(groups),
        "languages": [group["language"] for group in groups],
        "category_count": len(categories),
        "categories": categories,
        "search_query_count": len(search_queries),
        "playlist_id_count": len(playlist_ids),
        "target_track_count": payload.get("target_track_count", {}),
        "quality_targets": payload.get("quality_targets", {}),
    }


def playlist_ids_from_manifest(payload: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for group in payload["language_groups"]:
        ids.extend(str(playlist_id).strip() for playlist_id in group.get("playlist_ids", []) if str(playlist_id).strip())
    return list(dict.fromkeys(ids))


def search_queries_from_manifest(payload: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for group in payload["language_groups"]:
        language = group["language"]
        for query in group.get("spotify_search_queries", []):
            rows.append({"language": language, "query": str(query)})
    return rows


def write_playlist_id_file(payload: dict[str, Any], target: Path) -> int:
    ids = playlist_ids_from_manifest(payload)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(ids) + ("\n" if ids else ""), encoding="utf-8")
    return len(ids)


def write_search_query_file(payload: dict[str, Any], target: Path) -> int:
    rows = search_queries_from_manifest(payload)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["language", "query"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
