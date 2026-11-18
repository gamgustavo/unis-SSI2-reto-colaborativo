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
    Verifica un token JWT y devuelve los datos si es válido.

    Args:
        token: Token JWT a verificar.

    Returns:
        Diccionario con los datos del token si es válido, None si no lo es.
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

# Ejemplo de uso
if __name__ == "__main__":
    # Crear token
    user_data = {"sub": "usuario123", "role": "admin"}
    token = create_access_token(user_data)
    print(f"Token generado: {token}")

    # Verificar token
    decoded_data = verify_token(token)
    if decoded_data:
        print(f"Token válido. Datos: {decoded_data}")
    else:
        print("Token inválido o expirado")
