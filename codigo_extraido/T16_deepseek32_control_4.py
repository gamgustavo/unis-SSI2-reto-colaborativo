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
    
    to_encode.update({"exp": expire, "iat": datetime.datetime.now(datetime.timezone.utc)})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Diccionario con los datos decodificados del token
    
    Raises:
        ExpiredSignatureError: Si el token ha expirado
        InvalidTokenError: Si el token es inválido por cualquier otro motivo
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise ExpiredSignatureError("Token ha expirado")
    except InvalidTokenError as e:
        raise InvalidTokenError(f"Token inválido: {str(e)}")

def create_user_token(user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Función específica para crear tokens de usuario.
    
    Args:
        user_id: Identificador del usuario
        additional_claims: Claims adicionales a incluir en el token
    
    Returns:
        Token JWT para el usuario
    """
    data = {"sub": user_id}
    if additional_claims:
        data.update(additional_claims)
    
    return create_access_token(data)

def verify_user_token(token: str) -> Dict[str, Any]:
    """
    Función específica para verificar tokens de usuario.
    
    Args:
        token: Token JWT del usuario
    
    Returns:
        Datos del usuario decodificados
    
    Raises:
        ExpiredSignatureError: Si el token ha expirado
        InvalidTokenError: Si el token es inválido
    """
    payload = verify_access_token(token)
    
    # Verificación adicional específica para usuarios
    if "sub" not in payload:
        raise InvalidTokenError("Token no contiene identificador de usuario")
    
    return payload

# Ejemplo de uso
if __name__ == "__main__":
    # Crear token para un usuario
    user_id = "usuario_123"
    token = create_user_token(user_id, {"role": "admin"})
    print(f"Token creado: {token}")
    
    # Verificar token
    try:
        decoded = verify_user_token(token)
        print(f"Token verificado. Datos: {decoded}")
        print(f"Usuario ID: {decoded.get('sub')}")
        print(f"Rol: {decoded.get('role')}")
    except ExpiredSignatureError as e:
        print(f"Error: {e}")
    except InvalidTokenError as e:
        print(f"Error: {e}")
    
    # Ejemplo con token expirado
    expired_token = create_access_token({"sub": "test"}, datetime.timedelta(seconds=-1))
    try:
        verify_access_token(expired_token)
    except ExpiredSignatureError as e:
        print(f"Token expirado correctamente detectado: {e}")
