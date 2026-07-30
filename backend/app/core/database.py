from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

import os

# Carrega as variáveis do arquivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL não encontrada no arquivo .env")

# Cria a conexão com o PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Mostra os comandos SQL no terminal (útil durante o desenvolvimento)
)

# Cria a fábrica de sessões
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Classe base para os modelos do SQLAlchemy
class Base(DeclarativeBase):
    pass


# Dependência para uso nas rotas do FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()