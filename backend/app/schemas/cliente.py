from pydantic import BaseModel, EmailStr


class ClienteBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    carteirinha: str
    convenio: str
    endereco: str


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    ativo: bool = True


class ClienteResponse(ClienteBase):
    id: int
    ativo: bool

    class Config:
        from_attributes = True


Cliente = ClienteResponse
