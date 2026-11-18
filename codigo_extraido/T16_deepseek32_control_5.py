import jwt
import datetime
from typing import Optional, Dict, Any
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

# Configuración (en producción usar variables de entorno)
SECRET_KEY = "clave_secreta_super_segura_cambiar_en_produccion"
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

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
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
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Crea un token de refresco con mayor tiempo de expiración.
    
    Args:
        data: Diccionario con los datos a incluir en el token
    
    Returns:
        Token JWT de refresco
    """
    to_encode = data.copy()
    # Token de refresco válido por 7 días
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Genera un nuevo token de acceso usando un token de refresco válido.
    
    Args:
        refresh_token: Token de refresco
    
    Returns:
        Nuevo token de acceso o None si el token de refresco no es válido
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar que sea un token de refresco
        if payload.get("type") != "refresh":
            print("Error: No es un token de refresco válido")
            return None
        
        # Extraer datos del usuario (excluyendo campos específicos del token)
        user_data = {k: v for k, v in payload.items() if k not in ["exp", "iat", "type"]}
        
        # Crear nuevo token de acceso
        new_access_token = create_access_token(user_data)
        return new_access_token
        
    except ExpiredSignatureError:
        print("Error: El token de refresco ha expirado")
        return None
    except InvalidTokenError as e:
        print(f"Error: Token de refresco inválido - {e}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    # Datos de ejemplo del usuario
    user_data = {
        "sub": "12345",
        "username": "usuario_ejemplo",
        "email": "usuario@ejemplo.com",
        "role": "user"
    }
    
    # Crear token de acceso
    access_token = create_access_token(user_data)
    print(f"Token de acceso: {access_token}")
    
    # Verificar token
    decoded = verify_access_token(access_token)
    if decoded:
        print(f"Token válido. Datos: {decoded}")
    
    # Crear y usar token de refresco
    refresh_token = create_refresh_token({"sub": "12345"})
    print(f"\nToken de refresco: {refresh_token}")
    
    new_access_token = refresh_access_token(refresh_token)
    if new_access_token:
        print(f"Nuevo token de acceso: {new_access_token}")
    
    # Probar con token expirado (simulado)
    expired_token = create_access_token(user_data, expires_delta=datetime.timedelta(seconds=-1))
    print(f"\nVerificando token expirado: {verify_access_token(expired_token)}")
