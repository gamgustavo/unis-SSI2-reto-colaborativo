import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Configuración
SECRET_KEY = "tu_secreto_super_seguro"  # Cambia esto por una clave secreta segura en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.

    Args:
        data: Diccionario con los datos a codificar en el token.
        expires_delta: Tiempo de expiración del token. Si no se proporciona, usa el valor por defecto.

    Returns:
        Token JWT codificado como string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un token JWT.

    Args:
        token: Token JWT a verificar.

    Returns:
        Diccionario con los datos decodificados si el token es válido, None en caso contrario.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expirado")
        return None
    except jwt.InvalidTokenError:
        print("Token inválido")
        return None

def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos del usuario a partir de un token JWT.

    Args:
        token: Token JWT a decodificar.

    Returns:
        Diccionario con los datos del usuario si el token es válido, None en caso contrario.
    """
    payload = verify_token(token)
    if payload:
        return {
            "user_id": payload.get("sub"),
            "username": payload.get("username"),
            "scopes": payload.get("scopes", [])
        }
    return None
