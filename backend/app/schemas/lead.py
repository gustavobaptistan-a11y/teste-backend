from typing import Optional

from pydantic import BaseModel


class LeadBase(BaseModel):
    titulo: str
    cliente_nome: str
    valor: float
    etapa: str = "Novo Lead"
    descricao: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdateEtapa(BaseModel):
    etapa: str


class LeadResponse(LeadBase):
    id: int

    class Config:
        from_attributes = True


Lead = LeadResponse
