"""FastAPI entry point for AgriSense AI.

Run:  uvicorn app.main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import routes_chat, routes_payment, routes_trace
from app.memory.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables, warm up connections.
    init_db()
    yield
    # Shutdown: close resources if needed.


app = FastAPI(
    title="AgriSense AI",
    description="Autonomous agricultural advisor — Bdapps Agentic AI Hackathon.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_chat.router)
app.include_router(routes_trace.router)
app.include_router(routes_payment.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "service": "agrisense", "env": settings.app_env}
