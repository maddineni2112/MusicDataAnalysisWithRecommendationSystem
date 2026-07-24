from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="music_health"),
    path("", views.dashboard, name="music_dashboard"),
    path("music/", views.dashboard, name="music_dashboard_prefixed"),
    path("recommender/", views.recommender, name="music_recommender"),
    path("explorer/", views.explorer, name="music_explorer"),
    path("artists/", views.artists, name="music_artists"),
    path("model-insights/", views.model_insights, name="music_model_insights"),
    path("admin/", views.admin_ops, name="music_admin_ops"),
]
