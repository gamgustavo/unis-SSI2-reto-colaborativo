import os
import tempfile
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Union, Dict, Any
import json
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def save_report_to_temp_file(
    report_data: Union[str, bytes, Dict[str, Any]],
    file_extension: Optional[str] = None,
    prefix: str = "report_",
    sanitize_filename: bool = True
) -> str:
    """
    Guarda datos de un reporte en un archivo temporal de forma segura.
    
    Args:
        report_data: Datos del reporte. Puede ser string, bytes o diccionario.
        file_extension: Extensión opcional del archivo (ej: '.txt', '.json').
        prefix: Prefijo para el nombre del archivo temporal.
        sanitize_filename: Si True, sanitiza el prefijo para evitar path traversal.
    
    Returns:
        Ruta completa al archivo temporal creado.
    
    Raises:
        ValueError: Si los datos son inválidos o no se puede crear el archivo.
        OSError: Si hay problemas de permisos o sistema de archivos.
    """
    
    # Validación de entrada básica
    if report_data is None:
        raise ValueError("Los datos del reporte no pueden ser None")
    
    # Sanitizar el prefijo del nombre del archivo
    if sanitize_filename and prefix:
        # Remover caracteres peligrosos para nombres de archivo
        import re
        prefix = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', prefix)
        prefix = prefix[:50]  # Limitar longitud
    
    # Convertir datos a bytes
    try:
        if isinstance(report_data, dict):
            # Para diccionarios, usar JSON con encoding seguro
            data_bytes = json.dumps(
                report_data, 
                ensure_ascii=False, 
                separators=(',', ':')
            ).encode('utf-8')
        elif isinstance(report_data, str):
            data_bytes = report_data.encode('utf-8')
        elif isinstance(report_data, bytes):
            data_bytes = report_data
        else:
            raise ValueError(f"Tipo de datos no soportado: {type(report_data)}")
    except (UnicodeEncodeError, TypeError) as e:
        raise ValueError(f"Error al convertir datos a bytes: {e}")
    
    # Validar tamaño de datos (límite de 10MB por seguridad)
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    if len(data_bytes) > MAX_SIZE:
        raise ValueError(f"Los datos exceden el tamaño máximo permitido ({MAX_SIZE} bytes)")
    
    # Crear directorio temporal seguro
    temp_dir = None
    file_path = None
    file_descriptor = None
    
    try:
        # Crear directorio temporal con permisos seguros
        temp_dir = tempfile.mkdtemp(prefix="secure_report_")
        
        # Configurar permisos seguros en el directorio (solo propietario)
        os.chmod(temp_dir, 0o700)
        
        # Generar nombre de archivo único y seguro
        random_suffix = secrets.token_hex(8)
        safe_prefix = prefix or "report"
        
        # Construir nombre base del archivo
        base_name = f"{safe_prefix}{random_suffix}"
        
        # Añadir extensión si se proporciona
        if file_extension:
            # Sanitizar extensión
            if not file_extension.startswith('.'):
                file_extension = f".{file_extension}"
            # Limpiar extensión de caracteres peligrosos
            import re
            file_extension = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', file_extension)
            file_extension = file_extension[:20]  # Limitar longitud
            base_name += file_extension
        
        # Crear ruta completa
        file_path = os.path.join(temp_dir, base_name)
        
        # Verificar que no haya path traversal
        resolved_path = os.path.realpath(file_path)
        resolved_dir = os.path.realpath(temp_dir)
        if not resolved_path.startswith(resolved_dir):
            raise ValueError("Intento de path traversal detectado")
        
        # Escribir datos de forma segura
        # Usar modo binario para evitar problemas de encoding
        with open(file_path, 'wb') as f:
            f.write(data_bytes)
        
        # Configurar permisos seguros en el archivo (solo lectura para propietario)
        os.chmod(file_path, 0o400)
        
        # Verificar integridad de los datos escritos
        with open(file_path, 'rb') as f:
            written_data = f.read()
        
        if written_data != data_bytes:
            raise ValueError("Error de integridad: datos escritos no coinciden con los originales")
        
        # Calcular hash para verificación adicional
        data_hash = hashlib.sha256(data_bytes).hexdigest()
        logger.debug(f"Archivo creado: {file_path}, Hash SHA256: {data_hash[:16]}...")
        
        return file_path
        
    except Exception as e:
        # Limpieza en caso de error
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
        
        logger.error(f"Error al crear archivo temporal: {e}")
        raise
        
    finally:
        # Cerrar descriptor de archivo si está abierto
        if file_descriptor:
            try:
                os.close(file_descriptor)
            except OSError:
                pass


# Función auxiliar para limpieza segura
def secure_cleanup_temp_file(file_path: str) -> None:
    """
    Elimina de forma segura un archivo temporal y su directorio.
    
    Args:
        file_path: Ruta al archivo temporal a eliminar.
    """
    if not file_path or not os.path.exists(file_path):
        return
    
    try:
        # Eliminar archivo
        os.unlink(file_path)
        
        # Intentar eliminar el directorio padre si está vacío
        parent_dir = os.path.dirname(file_path)
        if (parent_dir and 
            os.path.exists(parent_dir) and 
            parent_dir.startswith(tempfile.gettempdir())):
            try:
                os.rmdir(parent_dir)
            except OSError:
                # El directorio no está vacío o no se puede eliminar
                pass
                
    except (OSError, PermissionError) as e:
        logger.warning(f"No se pudo eliminar el archivo temporal {file_path}: {e}")


# Ejemplo de uso (comentado)
if __name__ == "__main__":
    # Ejemplo 1: Guardar texto simple
    try:
        temp_file = save_report_to_temp_file(
            report_data="Este es un reporte de ejemplo",
            file_extension=".txt",
            prefix="mi_reporte_"
        )
        print(f"Archivo creado: {temp_file}")
        
        # Limpieza después de usar
        secure_cleanup_temp_file(temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Ejemplo 2: Guardar datos JSON
    try:
        report_dict = {
            "id": 123,
            "nombre": "Reporte de seguridad",
            "fecha": "2024-01-01",
            "datos": [1, 2, 3, 4, 5]
        }
        
        temp_file = save_report_to_temp_file(
            report_data=report_dict,
            file_extension=".json",
            prefix="json_report_"
        )
        print(f"Archivo JSON creado: {temp_file}")
        
        # Limpieza después de usar
        secure_cleanup_temp_file(temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
