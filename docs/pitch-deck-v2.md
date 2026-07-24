# Indian Music Intelligence Platform v2.0 Pitch Deck

Author: Sampath Naga Maddineni

## Slide 1: Title

Indian Music Intelligence Platform v2.0

Full-stack ML, analytics, and recommendation platform for Indian music discovery.

## Slide 2: Problem

Most music recommendation portfolio projects stop at notebook similarity demos.

This platform shows the larger engineering problem:

- collect and normalize data
- preserve lineage
- infer music intelligence labels
- expose dashboards and APIs
- evaluate recommendations
- support admin operations
- present through a live portfolio experience

## Slide 3: v1 to v2 Evolution

v1.0:

- PySpark notebook
- exploratory analysis
- regression, PCA similarity, clustering
- report and presentation

v2.0:

- PostgreSQL data platform
- FastAPI service
- Django portfolio shell
- admin data operations
- explained recommendations
- deployment-ready structure

## Slide 4: Product Demo Flow

Demo path:

1. Open portfolio project card.
2. Launch dashboard first.
3. Explore language, mood, popularity, and playlist analytics.
4. Search songs and inspect detail pages.
5. Run recommender with seed track and natural-language filters.
6. Review model insights.
7. Show Admin Ops for imports, quality checks, jobs, model runs, and label overrides.

## Slide 5: Architecture

Components:

- Existing portfolio project card
- Django music shell
- FastAPI API/ML service
- PostgreSQL
- Typer CLI jobs
- Docker Compose local environment
- Render/Railway deployment path

## Slide 6: Data Pipeline

Supported inputs:

- CSV tracks
- generic JSON tracks
- public playlist-style JSON
- Spotify playlist collection with credentials

Pipeline outputs:

- normalized tracks/artists/playlists
- raw snapshots
- source lineage
- inferred labels
- quality results

## Slide 7: Indian Music Focus

Initial language scope:

- Hindi
- Telugu
- Tamil
- Malayalam
- Kannada
- Punjabi
- Bengali
- Marathi

Music categories:

- film
- indie
- devotional
- classical
- folk
- pop
- rap/hip-hop

## Slide 8: Dashboard

Dashboard answers:

- Which languages dominate?
- Which moods and types appear most?
- What years and playlists are represented?
- How much official popularity data exists?
- How much recommender coverage exists?
- Where are data quality issues?

## Slide 9: Recommender

Hybrid scoring uses:

- language
- mood
- music type
- region
- release era
- official popularity
- diversity penalty
- owner label overrides

Every result includes:

- short reasons
- technical score breakdown

## Slide 10: Model Insights

Current evaluation stores:

- model run metadata
- recommendation runs
- recommendation results
- coverage
- average score
- seed-exclusion pass rate
- playlist holdout hit rate
- playlist holdout average rank

Future ML:

- TF-IDF
- sentence embeddings
- pgvector
- larger-scale playlist holdout evaluation

## Slide 11: Admin Ops

Owner/admin can:

- import data
- run quality checks
- evaluate recommender
- inspect job history
- inspect job detail events
- inspect model run metrics
- apply label overrides

## Slide 12: Backend/API Strength

Technical stack:

- FastAPI
- SQLAlchemy 2
- Alembic
- PostgreSQL
- Typer CLI
- pytest
- Docker
- Django shell
- Gunicorn/Uvicorn production entrypoints

## Slide 13: Portfolio Impact

This project demonstrates:

- Python backend engineering
- ML/data platform thinking
- data quality and lineage
- practical recommendation systems
- dashboard/product sense
- deployment readiness
- iterative v1-to-v2 project ownership

## Slide 14: Limitations

Current limitations:

- sample dataset is small
- Spotify collection requires credentials
- recommender is metadata-first
- no public accounts
- no audio playback
- no paid LLM query parser

## Slide 15: Next Steps

Planned next steps:

- collect larger Indian playlist dataset
- add TF-IDF and embedding similarity
- improve artist network
- deploy public demo
- refresh screenshots
- export report PDF
- convert this deck to PPT
