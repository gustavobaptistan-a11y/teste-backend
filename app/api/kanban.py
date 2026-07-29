from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.lead import Lead

router = APIRouter(prefix="/kanban", tags=["Kanban Comercial"])

# Banco de dados simulado em memória para os leads do funil de vendas
banco_de_leads_falso = [
    {
        "id": 1,
        "titulo": "Plano Clínico Família",
        "cliente_nome": "Maria Silva",
        "valor": 1500.00,
        "etapa": "Novo Lead",
        "descricao": "Interessada nos exames preventivos."
    },
    {
        "id": 2,
        "titulo": "Checkup Empresarial",
        "cliente_nome": "João Santos",
        "valor": 4500.00,
        "etapa": "Em Negociação",
        "descricao": "Aguardando aprovação do financeiro deles."
    }
]

@router.get("/", response_model=List[Lead])
def listar_leads():
    """
    Lista todos os leads/oportunidades do funil de vendas.
    """
    return banco_de_leads_falso

@router.post("/", response_model=Lead, status_code=status.HTTP_201_CREATED)
def criar_lead(lead: Lead):
    """
    Cria uma nova oportunidade no Kanban.
    """
    for l in banco_de_leads_falso:
        if l["id"] == lead.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um lead com este ID."
            )
    
    novo_lead = lead.dict()
    banco_de_leads_falso.append(novo_lead)
    return novo_lead

@router.patch("/{lead_id}/etapa", response_model=Lead)
def mover_lead(lead_id: int, nova_etapa: str):
    """
    Move um card (lead) para uma nova etapa do funil (ex: Em Negociação, Fechado).
    """
    for l in banco_de_leads_falso:
        if l["id"] == lead_id:
            l["etapa"] = nova_etapa
            return l
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Lead não encontrado."
    )

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_lead(lead_id: int):
    """
    Remove um lead do Kanban.
    """
    for index, l in enumerate(banco_de_leads_falso):
        if l["id"] == lead_id:
            banco_de_leads_falso.pop(index)
            return None
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Lead não encontrado para exclusão."
    )