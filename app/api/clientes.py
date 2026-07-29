from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.schemas.cliente import Cliente

router = APIRouter(prefix="/clientes", tags=["Gestão de Clientes"])

# Banco de dados simulado em memória para os clientes do teste
banco_de_clientes_falso = []

@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: Cliente):
    """
    Cadastra um novo cliente no sistema.
    """
    # Verifica se já existe cliente com o mesmo ID
    for c in banco_de_clientes_falso:
        if c.id == cliente.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente cadastrado com este ID."
            )
    
    banco_de_clientes_falso.append(cliente)
    return {
        "mensagem": "Cliente criado com sucesso!",
        "cliente": cliente
    }

@router.get("/", response_model=List[Cliente])
def listar_clientes(nome: Optional[str] = Query(None, description="Filtrar cliente por parte do nome")):
    """
    Lista todos os clientes cadastrados ou filtra por nome.
    """
    if nome:
        clientes_filtrados = [c for c in banco_de_clientes_falso if nome.lower() in c.nome.lower()]
        return clientes_filtrados
    return banco_de_clientes_falso

@router.get("/{cliente_id}", response_model=Cliente)
def detalhar_cliente(cliente_id: int):
    """
    Busca os detalhes de um cliente específico pelo ID.
    """
    for c in banco_de_clientes_falso:
        if c.id == cliente_id:
            return c
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Cliente não encontrado."
    )

@router.put("/{cliente_id}")
def editar_cliente(cliente_id: int, cliente_atualizado: Cliente):
    """
    Atualiza os dados de um cliente existente.
    """
    for index, c in enumerate(banco_de_clientes_falso):
        if c.id == cliente_id:
            banco_de_clientes_falso[index] = cliente_atualizado
            return {
                "mensagem": "Cliente atualizado com sucesso!",
                "cliente": cliente_atualizado
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Cliente não encontrado para atualização."
    )

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(cliente_id: int):
    """
    Remove um cliente do sistema pelo ID.
    """
    for index, c in enumerate(banco_de_clientes_falso):
        if c.id == cliente_id:
            banco_de_clientes_falso.pop(index)
            return None
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Cliente não encontrado para exclusão."
    )