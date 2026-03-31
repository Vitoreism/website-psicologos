import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os

# Em produção, essa chave devia vir de os.getenv("SECRET_KEY", "chave_secreta")
SECRET_KEY = os.getenv("SECRET_KEY", "elo_terapeutico_super_secret_key_jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 dias

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/psicologos/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Por favor, faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_psicologo(token: str = Depends(oauth2_scheme)) -> int:
    payload = verify_token(token)
    psicologo_id = payload.get("sub")
    if psicologo_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="As credenciais são inválidas ou o token não identifica o usuário.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return int(psicologo_id)
