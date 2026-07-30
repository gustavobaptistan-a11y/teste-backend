from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    permissao: Mapped[str] = mapped_column(String(50), nullable=False, default="Usuario Comum")
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ClienteModel(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    telefone: Mapped[str] = mapped_column(String(50), nullable=False)
    carteirinha: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    convenio: Mapped[str] = mapped_column(String(120), nullable=False)
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class LeadModel(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    cliente_nome: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    valor: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    etapa: Mapped[str] = mapped_column(String(80), nullable=False, default="Novo Lead", index=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
