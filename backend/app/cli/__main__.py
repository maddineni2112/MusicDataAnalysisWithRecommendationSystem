from pathlib import Path

import typer

from app.db.session import SessionLocal
from app.services.evaluation import evaluate_recommender
from app.services.imports import import_csv, import_json, import_playlist_json
from app.services.jobs import run_logged_job
from app.services.quality import run_quality_checks
from app.services.spotify import collect_spotify_playlists, read_playlist_ids

app = typer.Typer(help="Indian Music Intelligence Platform data and ML jobs.")
import_app = typer.Typer(help="Import datasets.")
quality_app = typer.Typer(help="Run data quality checks.")
recommender_app = typer.Typer(help="Build recommendation artifacts.")
models_app = typer.Typer(help="Train/evaluate models.")
collect_app = typer.Typer(help="Collect API data.")


@import_app.command("csv")
def import_csv_command(path: Path, source_name: str = "Local CSV import") -> None:
    with SessionLocal() as db:
        result = run_logged_job(db, job_type="import_csv", parameters={"path": str(path), "source_name": source_name}, handler=lambda: import_csv(db, path, source_name))
    typer.echo(result)


@import_app.command("json")
def import_json_command(path: Path, source_name: str = "Local JSON import") -> None:
    with SessionLocal() as db:
        result = run_logged_job(db, job_type="import_json", parameters={"path": str(path), "source_name": source_name}, handler=lambda: import_json(db, path, source_name))
    typer.echo(result)


@import_app.command("playlist-json")
def import_playlist_json_command(path: Path, source_name: str = "Public playlist JSON import") -> None:
    with SessionLocal() as db:
        result = run_logged_job(
            db,
            job_type="import_playlist_json",
            parameters={"path": str(path), "source_name": source_name},
            handler=lambda: import_playlist_json(db, path, source_name),
        )
    typer.echo(result)


@import_app.command("sql-dump")
def import_sql_dump_command(path: Path) -> None:
    typer.echo(f"Offline SQL dump conversion scaffold: {path}")


@quality_app.command("run")
def quality_run_command() -> None:
    with SessionLocal() as db:
        result = run_logged_job(
            db,
            job_type="quality_run",
            parameters={},
            handler=lambda: {"rows_written": len(run_quality_checks(db)), "failure_count": 0},
        )
    typer.echo(result)


@recommender_app.command("rebuild")
def recommender_rebuild_command() -> None:
    typer.echo("Hybrid recommender uses online scoring in this milestone; artifact rebuild is scaffolded.")


@models_app.command("train")
def models_train_command(seed_limit: int = 25, result_limit: int = 10) -> None:
    with SessionLocal() as db:
        result = run_logged_job(
            db,
            job_type="model_evaluation",
            parameters={"seed_limit": seed_limit, "result_limit": result_limit},
            handler=lambda: evaluate_recommender(db, seed_limit=seed_limit, result_limit=result_limit),
        )
    typer.echo(result)


@collect_app.command("spotify")
def collect_spotify_command(
    playlist_id: list[str] = typer.Option(None, "--playlist-id", help="Spotify playlist ID to collect. Repeat for multiple playlists."),
    playlist_file: Path | None = typer.Option(None, "--playlist-file", help="Text file with one Spotify playlist ID per line."),
    market: str = "IN",
    limit_per_playlist: int = 100,
) -> None:
    playlist_ids = read_playlist_ids(playlist_file, playlist_id)
    if not playlist_ids:
        typer.echo("Provide at least one --playlist-id or --playlist-file.")
        raise typer.Exit(code=1)
    with SessionLocal() as db:
        result = run_logged_job(
            db,
            job_type="spotify_collect",
            parameters={"playlist_ids": playlist_ids, "market": market, "limit_per_playlist": limit_per_playlist},
            handler=lambda: collect_spotify_playlists(db, playlist_ids=playlist_ids, market=market, limit_per_playlist=limit_per_playlist),
        )
    typer.echo(result)


app.add_typer(import_app, name="import")
app.add_typer(quality_app, name="quality")
app.add_typer(recommender_app, name="recommender")
app.add_typer(models_app, name="models")
app.add_typer(collect_app, name="collect")

if __name__ == "__main__":
    app()
