import jwt
import datetime

# Configuración de la clave secreta y el algoritmo
SECRET_KEY = "clave_secreta"
ALGORITHM = "HS256"

def generate_token(user_id: str, expires_delta: int = None) -> str:
    """
    Genera un token JWT para un usuario dado.

    Args:
        user_id (str): ID del usuario.
        expires_delta (int): Tiempo en minutos antes de que el token expire. Si es None, se establece una expiración por defecto.

    Returns:
        str: Token JWT generado.
    """
    to_encode = {"sub": user_id}
    if expires_delta:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)  # Expiración por defecto de 15 minutos
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verifica la validez de un token JWT.

    Args:
        token (str): Token JWT a verificar.

    Returns:
        dict: Datos decodificados del token si es válido, None si no es válido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token ha expirado
    except jwt.InvalidTokenError:
        return None  # Token no válido
