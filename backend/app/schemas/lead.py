from typing import Optional

from pydantic import BaseModel, ConfigDict


class LeadBase(BaseModel):
    titulo: str
    cliente_nome: str
    valor: float
    etapa: str = "Novo Lead"
    descricao: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(LeadBase):
    pass


class LeadUpdateEtapa(BaseModel):
    etapa: str


class LeadResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


Lead = LeadResponse
