import yaml
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

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
        
    Security considerations:
        1. Valida que el archivo exista y sea un archivo regular
        2. Verifica permisos de lectura
        3. Limita el tamaño del archivo (10MB por defecto)
        4. Usa SafeLoader para evitar ejecución de código arbitrario
        5. Valida la estructura básica del YAML
    """
    
    # Constantes de seguridad
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    try:
        # 1. Validación de la ruta
        path = Path(file_path)
        
        # Verificar que la ruta sea absoluta o relativa segura
        if path.is_absolute():
            # En producción, considerar restringir a directorios específicos
            pass
        
        # 2. Verificar que el archivo exista y sea un archivo regular
        if not path.exists():
            logger.error(f"El archivo no existe: {file_path}")
            return None
            
        if not path.is_file():
            logger.error(f"La ruta no es un archivo: {file_path}")
            return None
        
        # 3. Verificar permisos de lectura
        if not os.access(file_path, os.R_OK):
            logger.error(f"Sin permisos de lectura para: {file_path}")
            return None
        
        # 4. Verificar tamaño del archivo
        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            logger.error(f"Archivo demasiado grande: {file_size} bytes (máximo: {MAX_FILE_SIZE})")
            return None
        
        # 5. Verificar que no sea un archivo vacío
        if file_size == 0:
            logger.error("El archivo está vacío")
            return None
        
        # 6. Leer y procesar el archivo con SafeLoader
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Validación básica del contenido
            if not content.strip():
                logger.error("El archivo no contiene contenido válido")
                return None
            
            # Cargar YAML con SafeLoader para evitar ejecución de código
            try:
                config = yaml.safe_load(content)
            except yaml.YAMLError as e:
                logger.error(f"Error de sintaxis YAML: {e}")
                return None
            except Exception as e:
                logger.error(f"Error inesperado al cargar YAML: {e}")
                return None
        
        # 7. Validar que el resultado sea un diccionario
        if config is None:
            logger.warning("El archivo YAML está vacío o contiene solo comentarios")
            return {}
            
        if not isinstance(config, dict):
            logger.error("El archivo YAML no contiene un diccionario en la raíz")
            return None
        
        # 8. Validación adicional de contenido (opcional)
        # Aquí se pueden agregar validaciones específicas del dominio
        
        return config
        
    except (OSError, IOError) as e:
        logger.error(f"Error de E/S al leer el archivo: {e}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error de YAML: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return None

# Ejemplo de uso (comentado para evitar ejecución accidental)
if __name__ == "__main__":
    # Ejemplo de cómo usar la función
    # config = load_yaml_config("config.yaml")
    # if config:
    #     print("Configuración cargada exitosamente")
    # else:
    #     print("Error al cargar la configuración")
    pass
