from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models import LeadModel, UsuarioModel
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdateEtapa

router = APIRouter(prefix="/kanban", tags=["Kanban Comercial"])


@router.get("/", response_model=List[LeadResponse])
def listar_leads(
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_active_user),
):
    """Lista todos os leads/oportunidades do funil de vendas."""
    return db.query(LeadModel).order_by(LeadModel.id.asc()).all()


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
    return novo_lead


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
    return None
