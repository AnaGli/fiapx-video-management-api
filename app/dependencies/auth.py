from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError, jwt
import os

from app.database import SessionLocal
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM, jws_bearer

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

    print("========== JWT VALIDATION START ==========")

    print(f"Token object: {token}")

    if not token:
        print("Token object is None")

    if token and hasattr(token, "credentials"):
        print(f"Token credentials: {token.credentials}")

    if not token or not token.credentials:

        print("Token missing or empty")

        raise HTTPException(
            status_code=401,
            detail="Token required"
        )

    jwt_token = token.credentials

    print(f"JWT token: {jwt_token}")

    secret_key = os.getenv("SECRET_KEY")

    algorithm = os.getenv("EXTERNAL_JWS_ALGORITHM", "HS256")

    print(f"Algorithm: {algorithm}")

    print(f"Secret key: {secret_key}")

    if not secret_key:

        print("Secret key not configured")

        raise HTTPException(
            status_code=500,
            detail="JWS verification key not configured"
        )

    try:

        print("Decoding JWT...")

        payload = jwt.decode(
            jwt_token,
            secret_key,
            algorithms=[algorithm]
        )

        print("JWT decoded successfully")

        print(f"Payload: {payload}")

    except ExpiredSignatureError as ex:

        print("Token expired")

        print(str(ex))

        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except JWTError as ex:

        print("JWT validation error")

        print(str(ex))

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    except Exception as ex:

        print("Unexpected error during JWT decode")

        print(type(ex))

        print(str(ex))

        raise HTTPException(
            status_code=500,
            detail="Unexpected JWT validation error"
        )

    cpf = payload.get("cpf")

    print(f"CPF extracted from token: {cpf}")

    if not cpf:

        print("CPF claim missing")

        raise HTTPException(
            status_code=401,
            detail="Token missing cpf claim"
        )

    print("========== JWT VALIDATION SUCCESS ==========")

    return cpf
    """
    Valida JWT/JWS emitido pela Lambda Auth e retorna o CPF.
    """

    if not token or not token.credentials:
        raise HTTPException(
            status_code=401,
            detail="Token required"
        )

    jwt_token = token.credentials

    secret_key = os.getenv("EXTERNAL_JWS_SECRET")

    algorithm = os.getenv("EXTERNAL_JWS_ALGORITHM", "HS256")

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

    except ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    cpf = payload.get("cpf")

    if not cpf:

        raise HTTPException(
            status_code=401,
            detail="Token missing cpf claim"
        )

    return cpf