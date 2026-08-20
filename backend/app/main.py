from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import auth, teachers, parents, students, assignments, admin, common, websocket, files


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create MinIO bucket if not exists
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Tutoring Website API",
    description="家教平台后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(teachers.router, prefix="/api/v1")
app.include_router(parents.router, prefix="/api/v1")
app.include_router(students.router, prefix="/api/v1")
app.include_router(assignments.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(common.router, prefix="/api/v1")
app.include_router(websocket.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
