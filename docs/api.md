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
