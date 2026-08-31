from datetime import datetime, timedelata, timezone
from warnings import deprecated
from josa import jwtError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashed_password(password: str)-> str:
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+ timedelata(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )   
    to_encode.update({"exp":expire,"type":"access"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM) 

def decode_token(token:str) -> dict|None:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]

        )
        return payload
    except JWTError:
        return None