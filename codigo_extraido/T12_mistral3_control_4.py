import yaml
from typing import Dict, Any
import io

def leer_configuracion_yaml(contenido_archivo: bytes) -> Dict[str, Any]:
    """
    Lee un archivo de configuración YAML subido por el usuario y devuelve el diccionario resultante.

    Args:
        contenido_archivo: Contenido del archivo en bytes (como se recibe de un upload).

    Returns:
        Diccionario con la configuración parseada.

    Raises:
        yaml.YAMLError: Si el archivo YAML no es válido.
    """
    try:
        return yaml.safe_load(io.StringIO(contenido_archivo.decode('utf-8')))
    except UnicodeDecodeError:
        return yaml.safe_load(io.StringIO(contenido_archivo.decode('latin-1')))
