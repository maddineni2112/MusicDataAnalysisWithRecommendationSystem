# API

Public APIs are read-only and documented through FastAPI OpenAPI docs.

- `GET /api/health`
- `GET /api/tracks`
- `GET /api/tracks/{id}`
- `GET /api/artists`
- `GET /api/artists/{id}`
- `GET /api/playlists`
- `GET /api/dashboard/overview`
- `GET /api/dashboard/trends`
- `GET /api/recommendations`
- `GET /api/model-insights`
- `GET /api/data-quality/summary`

Admin APIs are protected by the current milestone's shared secret header and will evolve toward portfolio session/signed-token integration.

Local admin demo header:

```text
x-admin-token: change-me-local-only
```

The Django music shell exposes an Admin Ops page that can import the sample CSV, run quality checks, and display job history against these protected endpoints.
