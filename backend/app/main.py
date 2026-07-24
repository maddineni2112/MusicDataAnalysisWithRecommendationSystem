from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, public
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Indian Music Intelligence Platform API",
    version="2.0-alpha",
    description="Public read APIs and protected data-ops APIs for Indian music analytics and recommendations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public.router, prefix="/api", tags=["public"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
