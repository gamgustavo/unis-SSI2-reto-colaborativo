import xml.etree.ElementTree as ET
from defusedxml.ElementTree import fromstring
from typing import List, Dict, Optional
import logging

# Configuración básica de logging para registrar errores potenciales
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def extract_xml_items(xml_content: str) -> List[Dict[str, Optional[str]]]:
    """
    Extrae todos los elementos 'item' de un documento XML y devuelve sus valores y atributos.

    Args:
        xml_content: Cadena que contiene el documento XML.

    Returns:
        Lista de diccionarios donde cada diccionario representa un elemento 'item'
        con sus atributos y contenido de texto. Si ocurre un error, devuelve una lista vacía.

    Raises:
        ValueError: Si el XML está mal formado o contiene entidades externas peligrosas.
    """
    if not xml_content or not isinstance(xml_content, str):
        logger.error("Entrada XML inválida: debe ser una cadena no vacía.")
        return []

    try:
        # Usar defusedxml para prevenir ataques XXE (XML External Entity)
        root = fromstring(xml_content)
    except ET.ParseError as e:
        logger.error(f"Error al parsear el XML: {e}")
        raise ValueError("El documento XML está mal formado.") from e
    except Exception as e:
        logger.error(f"Error inesperado al procesar el XML: {e}")
        raise ValueError("Error al procesar el documento XML.") from e

    items = []

    for item in root.findall('.//item'):
        item_data: Dict[str, Optional[str]] = {
            'text': item.text.strip() if item.text else None,
            'tail': item.tail.strip() if item.tail else None,
            'attributes': {k: v for k, v in item.attrib.items()} if item.attrib else None
        }
        items.append(item_data)

    return items
