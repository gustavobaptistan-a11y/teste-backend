from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.api.usuarios import banco_de_usuarios_falso
from app.core.security import verificar_senha, criar_token_acesso, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Configura o esquema de segurança OAuth2 e diz ao Swagger onde buscar o token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/token")
def login_para_token_acesso(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica o usuário pelo e-mail (informado no campo 'username') e senha.
    Retorna o Token JWT de acesso.
    """
    usuario_encontrado = None
    for u in banco_de_usuarios_falso:
        if u["email"] == form_data.username:
            usuario_encontrado = u
            break
            
    if not usuario_encontrado or not verificar_senha(form_data.password, usuario_encontrado["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Gera o token JWT contendo o e-mail no payload (sub)
    access_token = criar_token_acesso(data={"sub": usuario_encontrado["email"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/perfil-protegido")
def rota_protegida(token: str = Depends(oauth2_scheme)):
    """
    Rota de exemplo para testar a segurança. 
    Só pode ser acessada se você estiver logado e com o token autorizado no Swagger.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    return {
        "mensagem": "Acesso autorizado com sucesso!",
        "usuario_logado": email
    }