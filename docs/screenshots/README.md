# Demo Screenshots

This folder is the target for local demo screenshots used in the report, pitch deck, and portfolio presentation.

Capture fresh screenshots after the local demo is running:

```powershell
.\scripts\local_demo.ps1 -SkipBuild
.\scripts\capture_demo_screenshots.ps1
```

If the portfolio service is not running at `http://127.0.0.1:8000/`, skip that screenshot:

```powershell
.\scripts\capture_demo_screenshots.ps1 -SkipPortfolio
```

Expected images:

- `dashboard.png`
- `songs.png`
- `artists.png`
- `recommender.png`
- `model-insights.png`
- `admin-ops.png`
- `portfolio-project-card.png`
