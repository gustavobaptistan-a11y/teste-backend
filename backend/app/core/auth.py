from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.cache import cache_key_exists
from app.core.database import get_db
from app.core.security import ALGORITHM, SECRET_KEY
from app.models import UsuarioModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def token_blacklist_key(jti: str) -> str:
    return f"auth:blacklist:{jti}"


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UsuarioModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nao foi possivel validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        jti = payload.get("jti")
        if email is None or jti is None:
            raise credentials_exception
        if cache_key_exists(token_blacklist_key(jti)):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
    if usuario is None:
        raise credentials_exception

    return usuario


def get_optional_current_user(
    token: str | None = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db),
) -> UsuarioModel | None:
    if token is None:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        jti = payload.get("jti")
        if email is None or jti is None:
            return None
        if cache_key_exists(token_blacklist_key(jti)):
            return None
    except JWTError:
        return None

    return db.query(UsuarioModel).filter(UsuarioModel.email == email).first()


def get_current_active_user(usuario: UsuarioModel = Depends(get_current_user)) -> UsuarioModel:
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inativo.",
        )
    return usuario


def get_current_admin_user(usuario: UsuarioModel = Depends(get_current_active_user)) -> UsuarioModel:
    if usuario.permissao != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return usuario
