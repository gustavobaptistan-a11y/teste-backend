from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteBase(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    email: EmailStr
    telefone: str = Field(min_length=8, max_length=32)
    empresa: str | None = Field(default=None, max_length=255)
    origem: str | None = Field(default=None, max_length=120)
    observacoes: str | None = Field(default=None, max_length=1000)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    ativo: bool = True


class ClienteResponse(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool


Cliente = ClienteResponse
