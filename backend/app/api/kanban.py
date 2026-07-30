from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.cache import DASHBOARD_METRICS_CACHE_KEY, delete_cache
from app.core.database import get_db
from app.models import LeadModel, UsuarioModel
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate, LeadUpdateEtapa

router = APIRouter(prefix="/kanban", tags=["Kanban Comercial"])


@router.get("/", response_model=List[LeadResponse])
def listar_leads(
    skip: int = Query(0, ge=0, description="Quantidade de registros ignorados"),
    limit: int = Query(50, ge=1, le=100, description="Limite de registros retornados"),
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Lista todos os leads/oportunidades do funil de vendas."""
    return db.query(LeadModel).order_by(LeadModel.id.asc()).offset(skip).limit(limit).all()


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def criar_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Cria uma nova oportunidade no Kanban."""
    novo_lead = LeadModel(**lead.model_dump())
    db.add(novo_lead)
    db.commit()
    db.refresh(novo_lead)
    delete_cache(DASHBOARD_METRICS_CACHE_KEY)
    return novo_lead


@router.get("/{lead_id}", response_model=LeadResponse)
def detalhar_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Busca uma oportunidade especifica pelo ID."""
    lead = db.get(LeadModel, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nao encontrado.",
        )
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
def editar_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Atualiza todos os dados comerciais de uma oportunidade."""
    lead = db.get(LeadModel, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nao encontrado para atualizacao.",
        )

    for campo, valor in payload.model_dump().items():
        setattr(lead, campo, valor)

    db.commit()
    db.refresh(lead)
    delete_cache(DASHBOARD_METRICS_CACHE_KEY)
    return lead


@router.patch("/{lead_id}/etapa", response_model=LeadResponse)
def mover_lead(
    lead_id: int,
    payload: LeadUpdateEtapa,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Move um card para uma nova etapa do funil."""
    lead = db.get(LeadModel, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nao encontrado.",
        )

    lead.etapa = payload.etapa
    db.commit()
    db.refresh(lead)
    delete_cache(DASHBOARD_METRICS_CACHE_KEY)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Remove um lead do Kanban."""
    lead = db.get(LeadModel, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nao encontrado para exclusao.",
        )

    db.delete(lead)
    db.commit()
    delete_cache(DASHBOARD_METRICS_CACHE_KEY)
    return None
