import yaml
from typing import Dict, Any

def leer_configuracion_yaml(contenido_archivo: str) -> Dict[str, Any]:
    """
    Lee un archivo de configuración YAML y devuelve su contenido como un diccionario.

    Args:
        contenido_archivo: Contenido del archivo YAML como string.

    Returns:
        Diccionario con la configuración leída del YAML.

    Raises:
        yaml.YAMLError: Si el contenido no es un YAML válido.
    """
    return yaml.safe_load(contenido_archivo)
