from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin_user
from app.core.database import get_db
from app.core.security import gerar_hash_senha
from app.models import UsuarioModel
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioPermissaoUpdate,
    UsuarioResponse,
    UsuarioStatusUpdate,
    UsuarioUpdate,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UsuarioResponse)
def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra usuario com senha protegida por hash."""
    usuario_existente = db.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado no sistema.",
        )

    total_usuarios = db.query(UsuarioModel).count()
    permissao_inicial = "Administrador" if total_usuarios == 0 else "Usuario Comum"

    novo_usuario = UsuarioModel(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha),
        permissao=permissao_inicial,
        ativo=True,
    )

    db.add(novo_usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado no sistema.",
        )

    db.refresh(novo_usuario)
    return novo_usuario


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_admin_user),
):
    """Lista usuarios cadastrados. Acesso administrativo."""
    return db.query(UsuarioModel).order_by(UsuarioModel.nome.asc()).all()


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def editar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: UsuarioModel = Depends(get_current_admin_user),
):
    """Edita dados administrativos de um usuario."""
    usuario = db.get(UsuarioModel, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado.")

    if usuario.id == admin.id and not payload.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voce nao pode desativar a propria conta.",
        )

    email_em_uso = (
        db.query(UsuarioModel)
        .filter(UsuarioModel.id != usuario_id, UsuarioModel.email == payload.email)
        .first()
    )
    if email_em_uso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado para outro usuario.",
        )

    for campo, valor in payload.model_dump().items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/permissao", response_model=UsuarioResponse)
def alterar_permissao(
    usuario_id: int,
    payload: UsuarioPermissaoUpdate,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_admin_user),
):
    """Altera permissao de acesso de um usuario."""
    usuario = db.get(UsuarioModel, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado.")

    usuario.permissao = payload.permissao
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/status", response_model=UsuarioResponse)
def alterar_status(
    usuario_id: int,
    payload: UsuarioStatusUpdate,
    db: Session = Depends(get_db),
    admin: UsuarioModel = Depends(get_current_admin_user),
):
    """Ativa ou desativa uma conta da equipe."""
    usuario = db.get(UsuarioModel, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado.")

    if usuario.id == admin.id and not payload.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voce nao pode desativar a propria conta.",
        )

    usuario.ativo = payload.ativo
    db.commit()
    db.refresh(usuario)
    return usuario
