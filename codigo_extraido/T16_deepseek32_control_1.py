import jwt
import datetime
from typing import Optional, Dict, Any
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

# Configuración
SECRET_KEY = "tu_clave_secreta_muy_segura_y_compleja_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.
    
    Args:
        data: Diccionario con los datos a incluir en el token (ej: {"sub": "user_id"})
        expires_delta: Tiempo de expiración personalizado. Si es None, usa el valor por defecto.
    
    Returns:
        Token JWT codificado como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Diccionario con los datos del token si es válido, None si no es válido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        print("Error: El token ha expirado")
        return None
    except InvalidTokenError as e:
        print(f"Error: Token inválido - {e}")
        return None

def create_user_token(user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Función específica para crear tokens de usuario.
    
    Args:
        user_id: Identificador del usuario
        additional_claims: Claims adicionales para incluir en el token
    
    Returns:
        Token JWT codificado como string
    """
    data = {"sub": user_id}
    if additional_claims:
        data.update(additional_claims)
    return create_access_token(data)

# Ejemplo de uso
if __name__ == "__main__":
    # Crear un token para un usuario
    user_id = "usuario_123"
    token = create_user_token(user_id, {"role": "admin"})
    print(f"Token generado: {token}")
    
    # Verificar el token
    payload = verify_token(token)
    if payload:
        print(f"Token válido. Payload: {payload}")
        print(f"Usuario ID: {payload.get('sub')}")
        print(f"Rol: {payload.get('role')}")
    else:
        print("Token inválido")
    
    # Ejemplo con token expirado (simulado)
    expired_token = jwt.encode(
        {"sub": "test", "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    print(f"\nVerificando token expirado: {verify_token(expired_token)}")
