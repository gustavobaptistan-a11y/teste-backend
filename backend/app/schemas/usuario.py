from typing import Literal

from pydantic import BaseModel, EmailStr, Field

PermissaoUsuario = Literal["Administrador", "Usuario Comum"]


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=128)


class UsuarioUpdate(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    email: EmailStr
    permissao: PermissaoUsuario
    ativo: bool


class UsuarioPermissaoUpdate(BaseModel):
    permissao: PermissaoUsuario


class UsuarioStatusUpdate(BaseModel):
    ativo: bool


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    permissao: PermissaoUsuario
    ativo: bool

    class Config:
        from_attributes = True
