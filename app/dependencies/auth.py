from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError, jwt
import os

from app.database import SessionLocal
from app.models.user import User
from app.core.security import jws_bearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
jws_bearer = HTTPBearer(auto_error=False)

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

def get_jws_cpf(token=Security(jws_bearer)) -> str:
    """
    Valida JWT/JWS emitido pela Lambda Auth e retorna o CPF.
    """


    if not token or not token.credentials:
        raise HTTPException(
            status_code=401,
            detail="Token required"
        )

    jwt_token = token.credentials

    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")

    if not secret_key:
        raise HTTPException(
            status_code=500,
            detail="JWS verification key not configured"
        )

    try:
        payload = jwt.decode(
            jwt_token,
            secret_key,
            algorithms=[algorithm]
        )

    except ExpiredSignatureError as ex:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except JWTError as ex:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail="Unexpected JWT validation error"
        )


    cpf = payload.get("cpf")
    if not cpf:
        raise HTTPException(
            status_code=401,
            detail="Token missing cpf claim"
        )

    return cpf