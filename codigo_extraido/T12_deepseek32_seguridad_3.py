import yaml
import os
from pathlib import Path
from typing import Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """
    Carga de forma segura un archivo YAML de configuración.
    
    Args:
        file_path: Ruta al archivo YAML
        
    Returns:
        Diccionario con la configuración cargada
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        PermissionError: Si no hay permisos para leer el archivo
        ValueError: Si el archivo está vacío o el contenido no es válido
        yaml.YAMLError: Si hay errores de sintaxis en el YAML
    """
    
    # Validaciones iniciales de seguridad
    if not file_path:
        raise ValueError("La ruta del archivo no puede estar vacía")
    
    # Normalizar y validar la ruta
    try:
        normalized_path = os.path.normpath(file_path)
        path_obj = Path(normalized_path)
    except Exception as e:
        raise ValueError(f"Ruta de archivo inválida: {e}")
    
    # Verificar que es un archivo (no un directorio)
    if not path_obj.is_file():
        raise FileNotFoundError(f"El archivo no existe: {normalized_path}")
    
    # Verificar permisos de lectura
    if not os.access(normalized_path, os.R_OK):
        raise PermissionError(f"No se tienen permisos para leer el archivo: {normalized_path}")
    
    # Verificar tamaño del archivo (límite de 10MB para prevenir DoS)
    max_size = 10 * 1024 * 1024  # 10 MB
    file_size = path_obj.stat().st_size
    if file_size > max_size:
        raise ValueError(f"El archivo es demasiado grande ({file_size} bytes). Máximo permitido: {max_size} bytes")
    
    # Verificar que el archivo no esté vacío
    if file_size == 0:
        raise ValueError("El archivo está vacío")
    
    # Cargar el contenido con SafeLoader para prevenir ejecución de código arbitrario
    try:
        with open(normalized_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Verificación básica de contenido (no debe contener caracteres nulos)
            if '\x00' in content:
                raise ValueError("El archivo contiene caracteres nulos, posible archivo binario")
            
            # Cargar YAML de forma segura
            config = yaml.safe_load(content)
            
            # Verificar que se cargó algo (no None para archivos vacíos o solo comentarios)
            if config is None:
                logger.warning("El archivo YAML está vacío o solo contiene comentarios")
                return {}
            
            # Asegurar que el resultado es un diccionario
            if not isinstance(config, dict):
                raise ValueError(f"El contenido YAML debe ser un diccionario, no {type(config).__name__}")
            
            return config
            
    except yaml.YAMLError as e:
        logger.error(f"Error de sintaxis YAML: {e}")
        raise
    except UnicodeDecodeError:
        raise ValueError("El archivo no es un archivo de texto válido (codificación UTF-8 esperada)")
    except IOError as e:
        logger.error(f"Error de E/S al leer el archivo: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al procesar el archivo: {e}")
        raise

# Ejemplo de uso (comentado para evitar ejecución accidental)
if __name__ == "__main__":
    # Ejemplo de cómo usar la función
    try:
        config = load_yaml_config("config.yaml")
        print("Configuración cargada exitosamente")
        print(f"Claves encontradas: {list(config.keys())}")
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
