# Architecture

The v2 platform uses a Django page shell, FastAPI service, and PostgreSQL database.

- Django owns portfolio-style pages, navigation, and owner-login integration.
- FastAPI owns public read APIs, recommender APIs, data-ops APIs, and ML service logic.
- PostgreSQL stores normalized music data, raw/source lineage, inferred labels, jobs, model runs, and cached outputs.
- React islands are mounted into Django templates for interactive dashboards, explorer tables, recommender panels, and admin widgets.

Preferred deployment is same-domain/subpath routing. Separate service URLs are acceptable when free-tier hosting makes subpath proxying impractical.

## Existing Portfolio Link

The separate portfolio repository remains the public entrypoint. Its project card for **Indian Music Intelligence Platform** uses a `demo` click behavior and opens the local or deployed dashboard first. The music repo owns the platform implementation; the portfolio repo owns the card, navigation, and recruiter-facing project entry.

## Admin Ops

The v2 shell includes a local Admin Ops page for owner workflows. It calls protected FastAPI endpoints with the configured admin token to import sample data, run data quality checks, and inspect persisted job history.
