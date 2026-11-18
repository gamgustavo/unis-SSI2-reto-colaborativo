import jwt
import datetime
from typing import Optional

SECRET_KEY = "your_secret_key_here"  # Cambia esto por una clave segura en producción
ALGORITHM = "HS256"

def generate_token(user_id: int, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = {"sub": str(user_id)}
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None or "exp" not in payload:
            return None
        return user_id
    except jwt.PyJWTError:
        return None
