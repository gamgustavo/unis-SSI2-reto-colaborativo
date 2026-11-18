import yaml
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_yaml_config(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Carga de forma segura un archivo YAML de configuración.
    
    Args:
        file_path: Ruta al archivo YAML
        
    Returns:
        Diccionario con la configuración o None si hay error
        
    Security considerations:
        1. Valida que el archivo exista y sea un archivo regular
        2. Limita el tamaño máximo del archivo (10MB por defecto)
        3. Usa SafeLoader de PyYAML para evitar ejecución de código arbitrario
        4. Valida la estructura básica del YAML
        5. Maneja excepciones específicas
    """
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB máximo
    
    try:
        # 1. Validar ruta de entrada
        if not file_path or not isinstance(file_path, str):
            logger.error("La ruta del archivo debe ser una cadena no vacía")
            return None
            
        # 2. Normalizar y validar la ruta
        path = Path(file_path).resolve()
        
        # 3. Verificar que el archivo exista y sea un archivo regular
        if not path.exists():
            logger.error(f"El archivo no existe: {file_path}")
            return None
            
        if not path.is_file():
            logger.error(f"La ruta no es un archivo: {file_path}")
            return None
            
        # 4. Verificar permisos de lectura
        if not os.access(path, os.R_OK):
            logger.error(f"No se tienen permisos de lectura para: {file_path}")
            return None
            
        # 5. Verificar tamaño del archivo
        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            logger.error(f"Archivo demasiado grande ({file_size} bytes). Máximo: {MAX_FILE_SIZE} bytes")
            return None
            
        # 6. Verificar extensión (validación básica)
        if path.suffix.lower() not in ['.yaml', '.yml']:
            logger.warning(f"El archivo no tiene extensión YAML estándar: {path.suffix}")
            
        # 7. Leer y parsear el archivo con SafeLoader
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Validación básica de contenido
            if not content.strip():
                logger.error("El archivo YAML está vacío")
                return None
                
            # Parsear con SafeLoader para evitar ejecución de código
            config = yaml.safe_load(content)
            
            # 8. Validar que el resultado sea un diccionario
            if config is None:
                logger.warning("El archivo YAML está vacío o solo contiene comentarios")
                return {}
                
            if not isinstance(config, dict):
                logger.error("El contenido YAML debe ser un diccionario en el nivel superior")
                return None
                
            logger.info(f"Archivo YAML cargado exitosamente: {file_path}")
            return config
            
    except yaml.YAMLError as e:
        logger.error(f"Error de sintaxis YAML en {file_path}: {str(e)}")
        return None
        
    except UnicodeDecodeError:
        logger.error(f"Error de codificación en {file_path}. Use UTF-8")
        return None
        
    except PermissionError:
        logger.error(f"Error de permisos al acceder a {file_path}")
        return None
        
    except OSError as e:
        logger.error(f"Error del sistema al leer {file_path}: {str(e)}")
        return None
        
    except Exception as e:
        logger.error(f"Error inesperado al procesar {file_path}: {str(e)}")
        return None

# Ejemplo de uso (comentado para evitar ejecución automática)
"""
if __name__ == "__main__":
    # Ejemplo de uso seguro
    config = load_yaml_config("config.yaml")
    if config:
        print("Configuración cargada:", config)
    else:
        print("Error al cargar la configuración")
"""
