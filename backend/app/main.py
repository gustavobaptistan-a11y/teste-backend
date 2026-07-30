from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.clientes import router as cliente_router
from app.api.dashboard import router as dashboard_router
from app.api.home import router as home_router
from app.api.kanban import router as kanban_router
from app.api.usuarios import router as usuarios_router
from app.core.database import Base, engine
from app import models

app = FastAPI(
    title="Lifeline One API",
    description="API oficial do sistema",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def criar_tabelas():
    Base.metadata.create_all(bind=engine)


app.include_router(home_router)
app.include_router(cliente_router)
app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(kanban_router)
app.include_router(dashboard_router)
