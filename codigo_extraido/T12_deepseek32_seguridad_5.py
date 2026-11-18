import yaml
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def load_yaml_config(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Carga de forma segura un archivo YAML de configuración.
    
    Args:
        file_path: Ruta al archivo YAML
        
    Returns:
        Diccionario con la configuración o None si hay error
        
    Raises:
        ValueError: Si el archivo no existe o la ruta es inválida
        yaml.YAMLError: Si el archivo YAML está mal formado
    """
    
    # Validaciones iniciales de seguridad
    if not file_path:
        raise ValueError("La ruta del archivo no puede estar vacía")
    
    # Normalizar y validar la ruta
    try:
        normalized_path = os.path.normpath(file_path)
        path_obj = Path(normalized_path)
    except Exception as e:
        logger.error(f"Error al procesar la ruta: {e}")
        raise ValueError(f"Ruta de archivo inválida: {file_path}")
    
    # Verificar que es un archivo (no directorio)
    if not path_obj.is_file():
        raise ValueError(f"La ruta no corresponde a un archivo: {file_path}")
    
    # Verificar extensión (opcional pero recomendado)
    if path_obj.suffix.lower() not in ['.yaml', '.yml']:
        logger.warning(f"El archivo no tiene extensión YAML: {file_path}")
    
    # Verificar tamaño del archivo (límite de 10MB por seguridad)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    try:
        file_size = path_obj.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"Archivo demasiado grande ({file_size} bytes). Límite: {MAX_FILE_SIZE} bytes")
    except OSError as e:
        logger.error(f"Error al verificar tamaño del archivo: {e}")
        raise ValueError(f"No se puede acceder al archivo: {file_path}")
    
    # Cargar el archivo con medidas de seguridad
    try:
        with open(normalized_path, 'r', encoding='utf-8') as file:
            # Usar SafeLoader para evitar ejecución de código arbitrario
            config = yaml.load(file, Loader=yaml.SafeLoader)
            
            # Validar que el resultado sea un diccionario
            if config is not None and not isinstance(config, dict):
                logger.warning("El archivo YAML no contiene un diccionario en la raíz")
                # Convertir a diccionario si es posible, o devolver vacío
                return {}
            
            return config or {}
            
    except yaml.YAMLError as e:
        logger.error(f"Error de sintaxis YAML: {e}")
        raise
    except UnicodeDecodeError as e:
        logger.error(f"Error de codificación del archivo: {e}")
        raise ValueError("El archivo no está codificado en UTF-8 válido")
    except OSError as e:
        logger.error(f"Error de E/S al leer el archivo: {e}")
        raise ValueError(f"No se puede leer el archivo: {file_path}")
    except Exception as e:
        logger.error(f"Error inesperado al cargar YAML: {e}")
        raise

# Ejemplo de uso (comentado para evitar ejecución automática)
if __name__ == "__main__":
    # Ejemplo de uso seguro
    try:
        config = load_yaml_config("config.yaml")
        if config:
            print("Configuración cargada exitosamente")
            # Procesar configuración aquí
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
