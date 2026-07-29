from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        from_attributes = True