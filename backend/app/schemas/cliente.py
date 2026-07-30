from pydantic import BaseModel, ConfigDict, EmailStr


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool


Cliente = ClienteResponse
