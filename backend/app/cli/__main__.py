from pathlib import Path

import typer

from app.db.session import SessionLocal
from app.services.imports import import_csv, import_json
from app.services.jobs import run_logged_job
from app.services.quality import run_quality_checks

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
def models_train_command() -> None:
    typer.echo("Model training scaffold ready for popularity prediction and playlist holdout evaluation.")


@collect_app.command("spotify")
def collect_spotify_command() -> None:
    typer.echo("Spotify collection requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.")


app.add_typer(import_app, name="import")
app.add_typer(quality_app, name="quality")
app.add_typer(recommender_app, name="recommender")
app.add_typer(models_app, name="models")
app.add_typer(collect_app, name="collect")

if __name__ == "__main__":
    app()
