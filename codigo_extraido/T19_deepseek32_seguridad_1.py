import hashlib
import hmac
import os
import time
from datetime import datetime
import json
import secrets
import string
from typing import Optional, Tuple
import logging
from logging.handlers import RotatingFileHandler

# Configuración de logging seguro
def setup_secure_logger(log_file: str = 'auth_log.json') -> logging.Logger:
    """Configura un logger seguro con rotación de archivos"""
    logger = logging.getLogger('auth_logger')
    logger.setLevel(logging.INFO)
    
    # Evitar handlers duplicados
    if not logger.handlers:
        # Rotación de logs para prevenir archivos demasiado grandes
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Formato estructurado para fácil análisis y evitar inyección
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "event": %(message)s}',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

class SecureAuthLogger:
    """Clase para manejo seguro de logs de autenticación"""
    
    def __init__(self, log_file: str = 'auth_log.json'):
        self.logger = setup_secure_logger(log_file)
        self.failed_attempts = {}
        self.max_attempts = 5
        self.lockout_time = 300  # 5 minutos en segundos
        
        # Clave para HMAC (debería estar en variables de entorno en producción)
        self.hmac_key = os.environ.get('LOG_HMAC_KEY', secrets.token_bytes(32))
    
    def _sanitize_input(self, data: str) -> str:
        """Sanitiza entrada para prevenir inyección en logs"""
        if not data:
            return ""
        # Escapar caracteres problemáticos para JSON
        return json.dumps(data)[1:-1]  # Remover comillas externas
    
    def _hash_sensitive_data(self, data: str) -> str:
        """Aplica hash HMAC a datos sensibles para logging"""
        if not data:
            return ""
        # Usar HMAC para hashear con clave secreta
        hmac_obj = hmac.new(self.hmac_key, data.encode('utf-8'), hashlib.sha256)
        return hmac_obj.hexdigest()[:16]  # Truncar para legibilidad
    
    def _check_rate_limit(self, username: str) -> bool:
        """Verifica límite de intentos fallidos"""
        now = time.time()
        user_record = self.failed_attempts.get(username)
        
        if user_record:
            attempts, lockout_until = user_record
            if now < lockout_until:
                return False
            
            # Resetear si el bloqueo expiró
            if now >= lockout_until:
                del self.failed_attempts[username]
        
        return True
    
    def _record_failed_attempt(self, username: str):
        """Registra intento fallido y aplica bloqueo si es necesario"""
        now = time.time()
        
        if username not in self.failed_attempts:
            self.failed_attempts[username] = [1, 0]
        else:
            attempts, _ = self.failed_attempts[username]
            attempts += 1
            
            if attempts >= self.max_attempts:
                # Bloquear usuario
                self.failed_attempts[username] = [attempts, now + self.lockout_time]
            else:
                self.failed_attempts[username] = [attempts, 0]
    
    def log_auth_attempt(
        self,
        username: str,
        password: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Registra un intento de autenticación de forma segura
        
        Args:
            username: Nombre de usuario
            password: Contraseña (se hashea para logging)
            success: Resultado del intento
            ip_address: Dirección IP del cliente (opcional)
            user_agent: User-Agent del cliente (opcional)
        
        Returns:
            bool: True si el intento está permitido (no bloqueado)
        """
        try:
            # Verificar límite de intentos
            if not success and not self._check_rate_limit(username):
                self._log_blocked_attempt(username, ip_address)
                return False
            
            # Sanitizar entradas
            safe_username = self._sanitize_input(username)
            
            # Hashear datos sensibles (nunca loguear contraseñas en claro)
            password_hash = self._hash_sensitive_data(password)
            ip_hash = self._hash_sensitive_data(ip_address) if ip_address else ""
            
            # Sanitizar user_agent
            safe_user_agent = self._sanitize_input(user_agent) if user_agent else ""
            
            # Crear evento de log estructurado
            log_event = {
                "username": safe_username,
                "password_hash": password_hash,
                "success": success,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "ip_hash": ip_hash,
                "user_agent": safe_user_agent,
                "event_type": "authentication"
            }
            
            # Registrar en JSON seguro
            self.logger.info(json.dumps(log_event))
            
            # Actualizar contador de intentos fallidos
            if not success:
                self._record_failed_attempt(username)
            
            return True
            
        except Exception as e:
            # Log de error interno sin exponer detalles sensibles
            error_event = {
                "error": "log_failure",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "message": "Error en registro de autenticación"
            }
            self.logger.error(json.dumps(error_event))
            return True  # Permitir autenticación a pesar de error de logging
    
    def _log_blocked_attempt(self, username: str, ip_address: Optional[str] = None):
        """Registra intento bloqueado por rate limiting"""
        try:
            safe_username = self._sanitize_input(username)
            ip_hash = self._hash_sensitive_data(ip_address) if ip_address else ""
            
            block_event = {
                "username": safe_username,
                "ip_hash": ip_hash,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": "rate_limit_blocked",
                "message": "Intento bloqueado por límite de intentos"
            }
            
            self.logger.warning(json.dumps(block_event))
        except Exception:
            pass  # Silenciar errores en logging de bloqueo

# Función de ejemplo para integración
def login(username: str, password: str, **kwargs) -> Tuple[bool, str]:
    """
    Función de inicio de sesión segura con logging
    
    Args:
        username: Nombre de usuario
        password: Contraseña
        **kwargs: Argumentos adicionales (ip_address, user_agent)
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    # Inicializar logger (en producción, usar singleton o inyección de dependencias)
    auth_logger = SecureAuthLogger()
    
    # Verificar que el intento esté permitido
    if not auth_logger.log_auth_attempt(username, password, False, **kwargs):
        return False, "Demasiados intentos fallidos. Por favor, espere 5 minutos."
    
    # Aquí iría la lógica real de autenticación
    # EJEMPLO: Verificar contra base de datos o servicio
    # NOTA: Nunca almacenar contraseñas en texto plano
    
    # Simulación de autenticación (reemplazar con lógica real)
    is_authenticated = authenticate_user(username, password)
    
    # Registrar resultado
    auth_logger.log_auth_attempt(username, password, is_authenticated, **kwargs)
    
    if is_authenticated:
        return True, "Autenticación exitosa"
    else:
        return False, "Credenciales inválidas"

# Función de ejemplo para autenticación (IMPLEMENTAR SEGÚN NECESIDAD)
def authenticate_user(username: str, password: str) -> bool:
    """
    Función de ejemplo para autenticación.
    EN PRODUCCIÓN: Implementar verificación segura contra base de datos.
    """
    # Ejemplo: Verificar contra variables de entorno (solo para demostración)
    # En producción, usar hash seguro (bcrypt, argon2) con salt
    
    # Nunca comparar contraseñas directamente
    # Usar comparación segura contra timing attacks
    stored_hash = os.environ.get(f"AUTH_HASH_{username.upper()}", "")
    
    if not stored_hash:
        return False
    
    # En producción, usar: bcrypt.checkpw(password.encode(), stored_hash.encode())
    # Para este ejemplo, simular con hash simple (NO USAR EN PRODUCCIÓN)
    try:
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        # Comparación segura contra timing attacks
        return hmac.compare_digest(input_hash, stored_hash)
    except Exception:
        return False

# Configuración de seguridad recomendada para producción
def security_setup():
    """Configuración de seguridad inicial"""
    # Verificar variables de entorno críticas
    required_env_vars = ['LOG_HMAC_KEY', 'SECRET_KEY']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"ADVERTENCIA: Variables de entorno faltantes: {missing_vars}")
        print("Generando claves temporales para desarrollo...")
        
        if 'LOG_HMAC_KEY' not in os.environ:
            os.environ['LOG_HMAC_KEY'] = secrets.token_urlsafe(32)
        
        if 'SECRET_KEY' not in os.environ:
            os.environ['SECRET_KEY'] = secrets.token_urlsafe(32)

# Inicializar configuración de seguridad
if __name__ == "__main__":
    security_setup()
    
    # Ejemplo de uso
    result, message = login(
        username="test_user",
        password="test_password",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0"
    )
    print(f"Resultado: {result}, Mensaje: {message}")
