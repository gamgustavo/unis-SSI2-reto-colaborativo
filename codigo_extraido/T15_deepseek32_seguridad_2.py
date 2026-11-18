import os
import tempfile
import logging
from typing import Optional, Dict, Any
import json
import hashlib
import secrets

# Configurar logging para auditoría
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_report_to_temp_file(
    report_data: Dict[str, Any],
    file_prefix: str = "report_",
    file_suffix: str = ".json",
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB límite
    validate_json: bool = True
) -> Optional[str]:
    """
    Guarda datos de un reporte en un archivo temporal de forma segura.
    
    Args:
        report_data: Diccionario con los datos del reporte
        file_prefix: Prefijo para el nombre del archivo temporal
        file_suffix: Sufijo para el archivo (extensión)
        max_file_size: Tamaño máximo permitido para el archivo en bytes
        validate_json: Si True, valida que los datos sean JSON serializables
    
    Returns:
        Ruta del archivo temporal creado o None si hay error
    
    Security considerations:
        - Usa tempfile con mkstemp para evitar race conditions
        - Valida el tamaño de los datos
        - Sanitiza nombres de archivo
        - Manejo seguro de errores
        - Permisos de archivo restringidos (0600)
        - Validación de entrada
        - Prevención de path traversal
        - Logging para auditoría
    """
    
    # Validación de entrada
    if not isinstance(report_data, dict):
        logger.error("El reporte debe ser un diccionario")
        return None
    
    if not report_data:
        logger.error("El reporte no puede estar vacío")
        return None
    
    # Sanitizar prefijo y sufijo para prevenir path traversal
    def sanitize_filename_part(part: str) -> str:
        """Sanitiza una parte del nombre de archivo"""
        # Remover caracteres peligrosos
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '..']
        for char in dangerous_chars:
            part = part.replace(char, '_')
        # Limitar longitud
        return part[:50]
    
    safe_prefix = sanitize_filename_part(file_prefix)
    safe_suffix = sanitize_filename_part(file_suffix)
    
    # Validar tamaño de datos antes de procesar
    try:
        data_size = len(json.dumps(report_data, ensure_ascii=False).encode('utf-8'))
        if data_size > max_file_size:
            logger.error(f"Datos exceden el tamaño máximo permitido: {data_size} > {max_file_size}")
            return None
    except (TypeError, ValueError) as e:
        logger.error(f"Error al serializar datos: {e}")
        return None
    
    # Crear archivo temporal de forma segura
    temp_file = None
    temp_file_path = None
    
    try:
        # Usar mkstemp para evitar race conditions
        fd, temp_file_path = tempfile.mkstemp(
            prefix=safe_prefix,
            suffix=safe_suffix,
            dir=None,  # Usar directorio temporal por defecto del sistema
            text=False  # Trabajar en modo binario
        )
        
        logger.info(f"Creando archivo temporal: {temp_file_path}")
        
        # Escribir datos de forma segura
        with os.fdopen(fd, 'wb') as temp_file:
            # Serializar datos con validación
            if validate_json:
                try:
                    serialized_data = json.dumps(
                        report_data,
                        ensure_ascii=False,
                        separators=(',', ':'),
                        default=str  # Manejar tipos no serializables
                    )
                except (TypeError, ValueError) as e:
                    logger.error(f"Error al serializar JSON: {e}")
                    os.unlink(temp_file_path)
                    return None
            else:
                # Si no se valida JSON, convertir a string de forma segura
                serialized_data = str(report_data)
            
            # Escribir datos con encoding UTF-8
            temp_file.write(serialized_data.encode('utf-8'))
            
            # Verificar que el archivo no exceda el tamaño máximo
            temp_file.seek(0, os.SEEK_END)
            actual_size = temp_file.tell()
            
            if actual_size > max_file_size:
                logger.error(f"Archivo excede tamaño máximo: {actual_size} > {max_file_size}")
                temp_file.close()
                os.unlink(temp_file_path)
                return None
            
            # Calcular hash para integridad
            temp_file.seek(0)
            file_hash = hashlib.sha256(temp_file.read()).hexdigest()
            logger.info(f"Hash SHA-256 del archivo: {file_hash}")
            
        # Establecer permisos seguros (solo propietario puede leer/escribir)
        os.chmod(temp_file_path, 0o600)
        
        # Verificar que el archivo fue creado correctamente
        if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
            logger.info(f"Reporte guardado exitosamente en: {temp_file_path}")
            return temp_file_path
        else:
            logger.error("El archivo temporal no se creó correctamente")
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return None
            
    except (IOError, OSError) as e:
        logger.error(f"Error de E/S al crear archivo temporal: {e}")
        # Limpieza en caso de error
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        return None
    
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        # Limpieza en caso de error
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        return None


# Función auxiliar para limpieza segura de archivos temporales
def secure_temp_file_cleanup(file_path: str) -> bool:
    """
    Elimina de forma segura un archivo temporal.
    
    Args:
        file_path: Ruta del archivo a eliminar
    
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    try:
        if not file_path or not os.path.exists(file_path):
            return False
        
        # Verificar que es un archivo temporal (opcional, basado en ubicación)
        temp_dir = tempfile.gettempdir()
        if not os.path.commonpath([temp_dir, os.path.dirname(file_path)]) == temp_dir:
            logger.warning(f"Intento de eliminar archivo fuera del directorio temporal: {file_path}")
            return False
        
        # Sobrescribir con datos aleatorios antes de eliminar (para datos sensibles)
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 0:
                with open(file_path, 'wb') as f:
                    # Sobrescribir con bytes aleatorios
                    f.write(secrets.token_bytes(file_size))
        except (IOError, OSError):
            pass  # Continuar con la eliminación incluso si falla la sobrescritura
        
        # Eliminar archivo
        os.unlink(file_path)
        
        # Verificar que fue eliminado
        if not os.path.exists(file_path):
            logger.info(f"Archivo eliminado de forma segura: {file_path}")
            return True
        else:
            logger.error(f"No se pudo eliminar el archivo: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error al eliminar archivo temporal: {e}")
        return False


# Ejemplo de uso (comentado)
if __name__ == "__main__":
    # Datos de ejemplo del reporte
    sample_report = {
        "id": "REP-2024-001",
        "timestamp": "2024-01-15T10:30:00Z",
        "type": "security_scan",
        "results": {
            "vulnerabilities": [],
            "warnings": ["Configuración no óptima"],
            "passed_checks": 42
        },
        "metadata": {
            "scanner_version": "2.1.0",
            "duration_seconds": 120.5
        }
    }
    
    # Guardar reporte en archivo temporal
    temp_path = save_report_to_temp_file(
        report_data=sample_report,
        file_prefix="security_report_",
        file_suffix=".json",
        max_file_size=5 * 1024 * 1024  # 5 MB
    )
    
    if temp_path:
        print(f"Reporte guardado en: {temp_path}")
        
        # Leer y mostrar contenido (solo para demostración)
        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Contenido del archivo:\n{content[:500]}...")  # Mostrar primeros 500 caracteres
        except Exception as e:
            print(f"Error al leer archivo: {e}")
        
        # Limpieza (en producción, esto debería manejarse según el caso de uso)
        # secure_temp_file_cleanup(temp_path)
    else:
        print("Error al guardar el reporte")
