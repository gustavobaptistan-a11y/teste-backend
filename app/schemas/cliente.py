
from pydantic import BaseModel

class Cliente(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    carteirinha: str
    convenio: str
    endereco: str