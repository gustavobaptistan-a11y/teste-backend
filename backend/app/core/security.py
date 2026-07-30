import os
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """Verifica se a senha pura corresponde ao hash armazenado."""
    return pwd_context.verify(senha_pura, senha_hash)


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash da senha usando bcrypt."""
    return pwd_context.hash(senha)


def criar_token_acesso(data: dict, expires_delta: timedelta | None = None) -> str:
    """Gera o token JWT de acesso com tempo de expiracao."""
    dados_para_codificar = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    dados_para_codificar.update({"exp": expire})
    return jwt.encode(dados_para_codificar, SECRET_KEY, algorithm=ALGORITHM)
