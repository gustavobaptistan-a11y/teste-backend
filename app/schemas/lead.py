from pydantic import BaseModel, EmailStr
from typing import Optional
#padrao kanban: Novo Lead
class Lead(BaseModel):
    id: int
    titulo: str
    cliente_nome: str
    valor: float
    etapa: str = "Novo Lead"
    descricao: Optional[str] = None