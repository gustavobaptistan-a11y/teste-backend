from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.clientes import router as cliente_router
from app.api.dashboard import router as dashboard_router
from app.api.home import router as home_router
from app.api.kanban import router as kanban_router
from app.api.usuarios import router as usuarios_router
from app.core.config import settings
from app.core.database import Base, engine
from app import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Lifeline One API",
    description="API oficial do sistema",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def adicionar_headers_seguranca(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(home_router)
app.include_router(cliente_router)
app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(kanban_router)
app.include_router(dashboard_router)
