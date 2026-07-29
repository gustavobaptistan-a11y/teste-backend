from fastapi import FastAPI

from app.api.clientes import router as cliente_router
from app.api.home import router as home_router
from app.api.usuarios import router as usuarios_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="Lifeline One API",
    description="API oficial do sistema",
    version="1.0.0",
    docs_url="/docs",          # Mantém o Swagger ativo
    redoc_url=None             # Opcional: desativa a documentação alternativa ReDoc se quiser
)

app.include_router(home_router)
app.include_router(cliente_router)
app.include_router(usuarios_router)
app.include_router(auth_router)