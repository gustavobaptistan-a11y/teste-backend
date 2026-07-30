from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

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
