from fastapi import APIRouter, HTTPException, status
from app.schemas.usuario import UsuarioResponse, UsuarioCreate
from app.core.security import gerar_hash_senha
from typing import List

router = APIRouter()


## PREPARAÇÃO PARA O BANCO DE DADOS REAL:
# Quando integrarmos com o PostgreSQL, esta lista
# será substituída pelas consultas usando o SQLAlchemy 
# e a sessão injetada via `Depends(get_db)`.
banco_de_usuarios_falso = []


@router.post("/usuarios", status_code=status.HTTP_201_CREATED, response_model=UsuarioResponse)
def cadastrar_usuario(usuario: UsuarioCreate):
    """Cadastra um novo usuário com hash de senha e retorna os dados do usuário criado (sem a senha)
    FUTURO BANCO DE DADOS: A senha será armazenada de forma segura no banco de dados, e não retornada na resposta.
    """
    # usuario_existente = db.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).first()
    # Verifica se o email já está cadastrado
    for u in banco_de_usuarios_falso:
        if u["email"] == usuario.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado no sistema"
            )
    
    # Gera o hash da senha antes de armazenar
    senha_criptografada = gerar_hash_senha(usuario.senha)
    
    # Cria um novo usuário simulado
    novo_usuario = {
        "id": len(banco_de_usuarios_falso) + 1,
        "nome": usuario.nome,
        "email": usuario.email,
        "senha_hash": senha_criptografada
    } 
    
    # Armazena o usuário no "banco de dados" falso
    banco_de_usuarios_falso.append(novo_usuario)
    
    return novo_usuario

#Importamos e reutilizamos lista de usuarios do schema UsuarioResponse para retornar a lista de usuários   
#(vamos atualizar para postgresql depois)
from app.api.usuarios import banco_de_usuarios_falso

@router.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios():
    """Retorna a lista de todos os usuários cadastrados"""
    return banco_de_usuarios_falso
    