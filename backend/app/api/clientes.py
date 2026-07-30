from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models import ClienteModel, UsuarioModel
from app.schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate

router = APIRouter(prefix="/clientes", tags=["Gestao de Clientes"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ClienteResponse)
def criar_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Cadastra um novo cliente no PostgreSQL."""
    novo_cliente = ClienteModel(**cliente.model_dump())
    db.add(novo_cliente)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ja existe um cliente com este email ou carteirinha.",
        )

    db.refresh(novo_cliente)
    return novo_cliente


@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(
    nome: Optional[str] = Query(None, description="Filtrar cliente por parte do nome"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo/inativo"),
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Lista clientes cadastrados ou filtra por nome."""
    query = db.query(ClienteModel)
    if nome:
        query = query.filter(ClienteModel.nome.ilike(f"%{nome}%"))
    if ativo is not None:
        query = query.filter(ClienteModel.ativo == ativo)
    return query.order_by(ClienteModel.nome.asc()).all()


@router.get("/{cliente_id}", response_model=ClienteResponse)
def detalhar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Busca os detalhes de um cliente pelo ID."""
    cliente = db.get(ClienteModel, cliente_id)
    if cliente:
        return cliente

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Cliente nao encontrado.",
    )


@router.put("/{cliente_id}", response_model=ClienteResponse)
def editar_cliente(
    cliente_id: int,
    cliente_atualizado: ClienteUpdate,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Atualiza os dados de um cliente existente."""
    cliente = db.get(ClienteModel, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado para atualizacao.",
        )

    conflito = (
        db.query(ClienteModel)
        .filter(
            ClienteModel.id != cliente_id,
            or_(
                ClienteModel.email == cliente_atualizado.email,
                ClienteModel.carteirinha == cliente_atualizado.carteirinha,
            ),
        )
        .first()
    )
    if conflito:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ja existe outro cliente com este email ou carteirinha.",
        )

    for campo, valor in cliente_atualizado.model_dump().items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Remove um cliente do sistema pelo ID."""
    cliente = db.get(ClienteModel, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado para exclusao.",
        )

    db.delete(cliente)
    db.commit()
    return None
