from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os

from app.database import SessionLocal
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive or not found")

    return user


def get_jws_cpf(token: str = Depends(oauth2_scheme)) -> str:
    """Verifica um token JWS vindo de outro serviço e retorna o `cpf` do claim.

    A implementação tenta usar primeiro a chave pública configurada em
    `EXTERNAL_JWS_PUBLIC_KEY` (PEM) ou, se não presente, `EXTERNAL_JWS_SECRET`.
    O algoritmo pode ser configurado com `EXTERNAL_JWS_ALGORITHM` (padrão 'RS256').
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token required")

    key = os.getenv("EXTERNAL_JWS_PUBLIC_KEY") or os.getenv("EXTERNAL_JWS_SECRET")
    alg = os.getenv("EXTERNAL_JWS_ALGORITHM") or "RS256"

    if not key:
        raise HTTPException(status_code=500, detail="JWS verification key not configured")

    try:
        payload = jwt.decode(token, key, algorithms=[alg])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid JWS token")

    cpf = payload.get("cpf")
    if not cpf:
        raise HTTPException(status_code=401, detail="Token missing cpf claim")

    return cpf
