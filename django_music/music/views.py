from django.conf import settings
from django.shortcuts import render


def base_context(active: str) -> dict:
    return {
        "active": active,
        "api_base_url": settings.API_BASE_URL,
        "portfolio_home_url": "http://127.0.0.1:8000/#home",
        "portfolio_projects_url": "http://127.0.0.1:8000/#projects",
        "github_url": "https://github.com/maddineni2112/MusicDataAnalysisWithRecommendationSystem",
    }


def dashboard(request):
    return render(request, "music/dashboard.html", base_context("dashboard"))


def recommender(request):
    return render(request, "music/recommender.html", base_context("recommender"))


def explorer(request):
    return render(request, "music/explorer.html", base_context("explorer"))


def artists(request):
    return render(request, "music/artists.html", base_context("artists"))


def model_insights(request):
    return render(request, "music/model_insights.html", base_context("model-insights"))


def admin_ops(request):
    return render(request, "music/admin_ops.html", base_context("admin"))
