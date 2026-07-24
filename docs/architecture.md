# Architecture

The v2 platform uses a Django page shell, FastAPI service, and PostgreSQL database.

- Django owns portfolio-style pages, navigation, and owner-login integration.
- FastAPI owns public read APIs, recommender APIs, data-ops APIs, and ML service logic.
- PostgreSQL stores normalized music data, raw/source lineage, inferred labels, jobs, model runs, and cached outputs.
- React islands are mounted into Django templates for interactive dashboards, explorer tables, recommender panels, and admin widgets.

Preferred deployment is same-domain/subpath routing. Separate service URLs are acceptable when free-tier hosting makes subpath proxying impractical.
