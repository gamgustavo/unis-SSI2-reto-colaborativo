import os
import tempfile
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import hashlib
import secrets

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_report_to_temp_file(
    report_data: Dict[str, Any],
    file_prefix: str = "report_",
    file_suffix: str = ".json",
    validate_json: bool = True,
    max_file_size: int = 10 * 1024 * 1024  # 10 MB límite por defecto
) -> Optional[str]:
    """
    Guarda datos de un reporte en un archivo temporal de forma segura.
    
    Args:
        report_data: Diccionario con los datos del reporte
        file_prefix: Prefijo para el nombre del archivo temporal
        file_suffix: Sufijo para el archivo (extensión)
        validate_json: Si es True, valida que los datos sean JSON serializables
        max_file_size: Tamaño máximo permitido para el archivo en bytes
    
    Returns:
        Ruta del archivo temporal creado o None si hay error
    
    Raises:
        ValueError: Si los datos no son válidos
        OSError: Si hay problemas de E/S
    """
    
    # Validaciones de entrada
    if not isinstance(report_data, dict):
        raise ValueError("Los datos del reporte deben ser un diccionario")
    
    if not report_data:
        raise ValueError("Los datos del reporte no pueden estar vacíos")
    
    # Validar tamaño máximo de datos (estimación)
    try:
        data_size = len(json.dumps(report_data, separators=(',', ':')))
        if data_size > max_file_size:
            raise ValueError(f"Los datos exceden el tamaño máximo permitido ({max_file_size} bytes)")
    except (TypeError, OverflowError) as e:
        raise ValueError(f"Error al serializar datos: {str(e)}")
    
    # Crear directorio temporal seguro
    temp_dir = None
    temp_file = None
    file_path = None
    
    try:
        # Crear directorio temporal con permisos restringidos
        temp_dir = tempfile.mkdtemp(prefix="secure_report_")
        
        # Configurar permisos seguros (solo propietario puede leer/escribir)
        os.chmod(temp_dir, 0o700)
        
        # Generar nombre de archivo seguro con componente aleatorio
        random_token = secrets.token_hex(8)
        safe_prefix = "".join(c for c in file_prefix if c.isalnum() or c in ('_', '-', '.'))
        safe_suffix = "".join(c for c in file_suffix if c.isalnum() or c in ('_', '-', '.'))
        
        filename = f"{safe_prefix}{random_token}{safe_suffix}"
        file_path = os.path.join(temp_dir, filename)
        
        # Validar que la ruta esté dentro del directorio temporal
        temp_dir_path = Path(temp_dir).resolve()
        file_path_obj = Path(file_path).resolve()
        
        if temp_dir_path not in file_path_obj.parents:
            raise SecurityError("Intento de path traversal detectado")
        
        # Serializar datos con configuración segura
        if validate_json:
            # Validar que los datos sean JSON serializables
            try:
                json.dumps(report_data, separators=(',', ':'))
            except (TypeError, ValueError) as e:
                raise ValueError(f"Datos no válidos para JSON: {str(e)}")
        
        # Escribir archivo con manejo seguro
        with open(file_path, 'w', encoding='utf-8') as f:
            # Configurar permisos del archivo (solo propietario)
            os.chmod(file_path, 0o600)
            
            # Escribir datos con separadores seguros
            json.dump(
                report_data,
                f,
                separators=(',', ':'),  # Minimizar tamaño, evitar pretty print
                ensure_ascii=False,     # Permitir Unicode
                check_circular=True     # Detectar referencias circulares
            )
        
        # Verificar integridad del archivo
        with open(file_path, 'rb') as f:
            file_content = f.read()
            if len(file_content) > max_file_size:
                raise ValueError(f"Archivo excede el tamaño máximo permitido")
        
        logger.info(f"Reporte guardado exitosamente en: {file_path}")
        return file_path
        
    except (IOError, OSError, ValueError, SecurityError) as e:
        logger.error(f"Error al guardar reporte: {str(e)}")
        
        # Limpieza segura en caso de error
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError:
                pass
        
        if temp_dir and os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass
        
        raise
    
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        
        # Limpieza segura
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError:
                pass
        
        if temp_dir and os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass
        
        raise RuntimeError(f"Error al procesar el reporte: {str(e)}")

class SecurityError(Exception):
    """Excepción para errores de seguridad"""
    pass

# Función auxiliar para limpieza segura de archivos temporales
def secure_cleanup(file_path: str) -> None:
    """
    Elimina de forma segura un archivo temporal y su directorio.
    
    Args:
        file_path: Ruta del archivo a eliminar
    """
    try:
        if os.path.exists(file_path):
            # Sobrescribir con datos aleatorios antes de eliminar (opcional para datos sensibles)
            if os.path.getsize(file_path) > 0:
                with open(file_path, 'wb') as f:
                    f.write(secrets.token_bytes(os.path.getsize(file_path)))
            
            os.unlink(file_path)
            
            # Intentar eliminar el directorio padre si está vacío y es temporal
            parent_dir = os.path.dirname(file_path)
            if parent_dir and "tmp" in parent_dir:
                try:
                    os.rmdir(parent_dir)
                except OSError:
                    pass  # El directorio no está vacío, es normal
                    
    except OSError as e:
        logger.warning(f"No se pudo limpiar el archivo {file_path}: {str(e)}")

# Ejemplo de uso (comentado)
if __name__ == "__main__":
    try:
        # Datos de ejemplo
        sample_report = {
            "id": "report_001",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {
                "metric1": 123.45,
                "metric2": "valor seguro",
                "items": ["item1", "item2", "item3"]
            }
        }
        
        # Guardar reporte
        temp_file_path = save_report_to_temp_file(
            sample_report,
            file_prefix="financial_report_",
            file_suffix=".json",
            max_file_size=5 * 1024 * 1024  # 5 MB
        )
        
        print(f"Reporte guardado en: {temp_file_path}")
        
        # Limpieza después de usar
        # secure_cleanup(temp_file_path)
        
    except Exception as e:
        print(f"Error: {str(e)}")
