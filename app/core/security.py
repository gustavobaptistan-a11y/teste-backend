from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

# Configurações do JWT 
SECRET_KEY = "sua_chave_secreta_super_segura_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configura o passlib para usar algoritmo bcrypt para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """Verifica se a senha pura corresponde ao hash da senha"""
    return pwd_context.verify(senha_pura, senha_hash)

def gerar_hash_senha(senha: str) -> str:
    """Gera o hash da senha usando bcrypt"""
    return pwd_context.hash(senha)

def criar_token_acesso(data: dict, expires_delta: timedelta | None = None) -> str:
    """Gera o Token JWT de acesso com tempo de expiração"""
    dados_para_codificar = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    dados_para_codificar.update({"exp": expire})
    token_jwt = jwt.encode(dados_para_codificar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt