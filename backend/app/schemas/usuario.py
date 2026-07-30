from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PermissaoUsuario = Literal["Administrador", "Usuario Comum"]


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("senha")
    @classmethod
    def validar_forca_senha(cls, senha: str) -> str:
        if not any(char.islower() for char in senha):
            raise ValueError("A senha deve conter ao menos uma letra minuscula.")
        if not any(char.isupper() for char in senha):
            raise ValueError("A senha deve conter ao menos uma letra maiuscula.")
        if not any(char.isdigit() for char in senha):
            raise ValueError("A senha deve conter ao menos um numero.")
        return senha


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    permissao: PermissaoUsuario
    ativo: bool
