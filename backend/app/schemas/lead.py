from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

EtapaLead = Literal["Novo Lead", "Em Negociacao", "Proposta Enviada", "Fechado"]


class LeadBase(BaseModel):
    titulo: str = Field(min_length=2, max_length=255)
    cliente_nome: str = Field(min_length=2, max_length=255)
    valor: float = Field(ge=0)
    etapa: EtapaLead = "Novo Lead"
    descricao: Optional[str] = Field(default=None, max_length=1000)


class LeadCreate(LeadBase):
    pass


class LeadUpdate(LeadBase):
    pass


class LeadUpdateEtapa(BaseModel):
    etapa: EtapaLead


class LeadResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


Lead = LeadResponse
