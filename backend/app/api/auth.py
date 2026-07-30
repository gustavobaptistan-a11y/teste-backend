from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, oauth2_scheme, token_blacklist_key
from app.core.cache import set_cache_key
from app.core.database import get_db
from app.core.security import ALGORITHM, SECRET_KEY, criar_token_acesso, gerar_hash_senha, verificar_senha
from app.models import UsuarioModel
from app.schemas.usuario import UsuarioResponse, UsuarioTrocaSenha

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/token")
def login_para_token_acesso(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Autentica por e-mail e senha, retornando um token JWT."""
    usuario = db.query(UsuarioModel).filter(UsuarioModel.email == form_data.username).first()
    if not usuario or not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inativo.",
        )

    access_token = criar_token_acesso(data={"sub": usuario.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": UsuarioResponse.model_validate(usuario),
    }


@router.get("/me", response_model=UsuarioResponse)
def obter_perfil(usuario: UsuarioModel = Depends(get_current_active_user)):
    """Retorna os dados do usuario autenticado."""
    return usuario


@router.put("/trocar-senha")
def trocar_senha(
    payload: UsuarioTrocaSenha,
    token: str = Depends(oauth2_scheme),
    usuario: UsuarioModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Troca a senha do usuario autenticado apos validar a senha atual."""
    if not verificar_senha(payload.senha_atual, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta.",
        )

    if verificar_senha(payload.nova_senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ser diferente da senha atual.",
        )

    usuario.senha_hash = gerar_hash_senha(payload.nova_senha)
    db.commit()

    payload_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    jti = payload_token.get("jti")
    exp = payload_token.get("exp")
    if jti and exp:
        ttl_seconds = max(int(exp - datetime.now(UTC).timestamp()), 1)
        set_cache_key(token_blacklist_key(jti), "revoked", ttl_seconds)

    return {"mensagem": "Senha alterada com sucesso. Faca login novamente."}


@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Revoga o token atual ate sua expiracao natural."""
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token sem identificador de sessao.",
        )

    ttl_seconds = max(int(exp - datetime.now(UTC).timestamp()), 1)
    revoked = set_cache_key(token_blacklist_key(jti), "revoked", ttl_seconds)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis indisponivel para revogacao de token.",
        )

    return {"mensagem": "Sessao encerrada com sucesso."}
