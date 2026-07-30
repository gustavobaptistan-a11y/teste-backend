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


class UsuarioTrocaSenha(BaseModel):
    senha_atual: str = Field(min_length=1, max_length=128)
    nova_senha: str = Field(min_length=8, max_length=128)
    confirmar_nova_senha: str = Field(min_length=8, max_length=128)

    @field_validator("nova_senha")
    @classmethod
    def validar_forca_nova_senha(cls, senha: str) -> str:
        return UsuarioCreate.validar_forca_senha(senha)

    @field_validator("confirmar_nova_senha")
    @classmethod
    def validar_confirmacao(cls, confirmar_nova_senha: str, info) -> str:
        nova_senha = info.data.get("nova_senha")
        if nova_senha and confirmar_nova_senha != nova_senha:
            raise ValueError("A confirmacao deve ser igual a nova senha.")
        return confirmar_nova_senha


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    permissao: PermissaoUsuario
    ativo: bool
