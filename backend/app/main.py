from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, public

app = FastAPI(
    title="Indian Music Intelligence Platform API",
    version="2.0-alpha",
    description="Public read APIs and protected data-ops APIs for Indian music analytics and recommendations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public.router, prefix="/api", tags=["public"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
