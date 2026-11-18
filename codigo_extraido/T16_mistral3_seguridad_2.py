import os
import jwt
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Configuración segura de JWT
class JWTConfig:
    # Generar claves RSA en tiempo de ejecución (en producción, estas deberían ser persistentes y seguras)
    _private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    _public_key = _private_key.public_key()

    # Obtener las claves en formato PEM
    PRIVATE_KEY = _private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    PUBLIC_KEY = _public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Configuración segura
    ALGORITHM = "RS256"  # Algoritmo asimétrico recomendado
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Tiempo de expiración corto para tokens de acceso
    REFRESH_TOKEN_EXPIRE_DAYS = 7  # Tiempo de expiración más largo para tokens de refresco
    ISSUER = "auth_service"  # Identificador del emisor
    AUDIENCE = "user_client"  # Identificador de la audiencia

    # Lista de claims críticos que no deben ser modificados
    CRITICAL_CLAIMS = {"exp", "iss", "aud", "sub", "iat", "nbf", "jti"}

def generate_jwt_token(
    user_id: str,
    username: str,
    token_type: str = "access",
    additional_claims: Optional[Dict[str, Any]] = None,
    jti: Optional[str] = None
) -> str:
    """
    Genera un token JWT seguro con claims estándar y personalizados.

    Args:
        user_id: Identificador único del usuario
        username: Nombre de usuario
        token_type: Tipo de token ("access" o "refresh")
        additional_claims: Claims adicionales a incluir en el token
        jti: Identificador único del token (opcional)

    Returns:
        Token JWT codificado
    """
    if additional_claims is None:
        additional_claims = {}

    # Validar token_type
    if token_type not in ("access", "refresh"):
        raise ValueError("token_type debe ser 'access' o 'refresh'")

    # Configurar tiempo de expiración según el tipo de token
    if token_type == "access":
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS)

    # Generar JTI si no se proporciona
    if jti is None:
        jti = os.urandom(16).hex()

    # Claims estándar
    payload = {
        "sub": str(user_id),  # Subject (identificador del usuario)
        "username": username,
        "iss": JWTConfig.ISSUER,  # Issuer
        "aud": JWTConfig.AUDIENCE,  # Audience
        "iat": int(time.time()),  # Issued at
        "nbf": int(time.time()),  # Not before
        "exp": int(expire.timestamp()),  # Expiration time
        "jti": jti,  # JWT ID
        "token_type": token_type,
    }

    # Validar que los claims adicionales no sobrescriban los críticos
    for claim in additional_claims:
        if claim in JWTConfig.CRITICAL_CLAIMS:
            raise ValueError(f"El claim '{claim}' está reservado y no puede ser modificado")

    # Combinar claims
    payload.update(additional_claims)

    # Generar token con firma RSA
    token = jwt.encode(
        payload,
        JWTConfig.PRIVATE_KEY,
        algorithm=JWTConfig.ALGORITHM
    )

    return token

def verify_jwt_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verifica y decodifica un token JWT.

    Args:
        token: Token JWT a verificar
        token_type: Tipo de token esperado ("access" o "refresh")

    Returns:
        Diccionario con los claims del token

    Raises:
        jwt.ExpiredSignatureError: Si el token ha expirado
        jwt.InvalidTokenError: Si el token es inválido por cualquier otra razón
    """
    try:
        # Decodificar y verificar el token
        payload = jwt.decode(
            token,
            JWTConfig.PUBLIC_KEY,
            algorithms=[JWTConfig.ALGORITHM],
            issuer=JWTConfig.ISSUER,
            audience=JWTConfig.AUDIENCE,
            options={
                "require": ["exp", "iss", "aud", "sub", "iat", "nbf", "jti"],
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
                "verify_signature": True,
            }
        )

        # Verificar tipo de token
        if payload.get("token_type") != token_type:
            raise jwt.InvalidTokenError(f"Token type mismatch. Expected {token_type}")

        # Verificar que no se hayan modificado claims críticos
        for claim in JWTConfig.CRITICAL_CLAIMS:
            if claim not in payload:
                raise jwt.InvalidTokenError(f"Missing critical claim: {claim}")

        return payload

    except jwt.PyJWTError as e:
        # Manejar diferentes tipos de errores de JWT
        if isinstance(e, jwt.ExpiredSignatureError):
            raise jwt.ExpiredSignatureError("Token has expired") from e
        elif isinstance(e, jwt.InvalidAudienceError):
            raise jwt.InvalidTokenError("Invalid audience") from e
        elif isinstance(e, jwt.InvalidIssuerError):
            raise jwt.InvalidTokenError("Invalid issuer") from e
        elif isinstance(e, jwt.InvalidSignatureError):
            raise jwt.InvalidTokenError("Invalid signature") from e
        else:
            raise jwt.InvalidTokenError("Invalid token") from e

def generate_token_pair(user_id: str, username: str) -> Dict[str, str]:
    """
    Genera un par de tokens (access y refresh) para un usuario.

    Args:
        user_id: Identificador único del usuario
        username: Nombre de usuario

    Returns:
        Diccionario con los tokens de acceso y refresco
    """
    # Generar tokens con el mismo JTI para el par
    jti = os.urandom(16).hex()

    access_token = generate_jwt_token(
        user_id=user_id,
        username=username,
        token_type="access",
        jti=jti
    )

    refresh_token = generate_jwt_token(
        user_id=user_id,
        username=username,
        token_type="refresh",
        jti=jti
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }

def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    """
    Refresca un token de acceso usando un token de refresco válido.

    Args:
        refresh_token: Token de refresco válido

    Returns:
        Diccionario con el nuevo token de acceso

    Raises:
        jwt.InvalidTokenError: Si el token de refresco es inválido
    """
    # Verificar el token de refresco
    payload = verify_jwt_token(refresh_token, token_type="refresh")

    # Generar un nuevo token de acceso
    new_access_token = generate_jwt_token(
        user_id=payload["sub"],
        username=payload["username"],
        token_type="access",
        jti=payload["jti"]  # Usar el mismo JTI que el token de refresco
    )

    return {
        "access_token": new_access_token,
        "token_type": "Bearer"
    }

# Ejemplo de uso seguro (no incluido en producción)
if __name__ == "__main__":
    # Generar un par de tokens para un usuario
    tokens = generate_token_pair("12345", "usuario_ejemplo")
    print("Tokens generados:")
    print(f"Access Token: {tokens['access_token'][:20]}...")
    print(f"Refresh Token: {tokens['refresh_token'][:20]}...")

    # Verificar el access token
    try:
        payload = verify_jwt_token(tokens["access_token"], "access")
        print("\nAccess Token válido:")
        print(f"Usuario: {payload['username']}")
        print(f"Expira en: {datetime.fromtimestamp(payload['exp'], timezone.utc)}")
    except jwt.PyJWTError as e:
        print(f"Error verificando token: {e}")

    # Refrescar el access token
    try:
        new_tokens = refresh_access_token(tokens["refresh_token"])
        print("\nNuevo Access Token generado:")
        print(f"Access Token: {new_tokens['access_token'][:20]}...")
    except jwt.PyJWTError as e:
        print(f"Error refrescando token: {e}")
