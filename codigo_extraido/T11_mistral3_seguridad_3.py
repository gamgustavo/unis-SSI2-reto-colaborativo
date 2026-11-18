import xml.etree.ElementTree as ET
from defusedxml.ElementTree import fromstring
from typing import List, Dict, Optional
import logging

# Configuración básica de logging para registrar posibles errores
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def extract_xml_items(xml_string: str) -> List[Dict[str, Optional[str]]]:
    """
    Extrae los valores de todos los elementos 'item' en un documento XML.

    Args:
        xml_string: Cadena que contiene el documento XML.

    Returns:
        Lista de diccionarios con los valores de los elementos 'item' y sus atributos.
        Cada diccionario contiene las claves 'value' (texto del elemento) y 'attributes'
        (diccionario de atributos del elemento).

    Raises:
        ValueError: Si el XML está mal formado o contiene entidades externas peligrosas.
        ET.ParseError: Si hay errores de parsing en el XML.
    """
    if not xml_string or not isinstance(xml_string, str):
        logger.error("Entrada inválida: xml_string debe ser una cadena no vacía.")
        raise ValueError("El documento XML debe ser una cadena no vacía.")

    try:
        # Usar defusedxml para prevenir ataques XXE (XML External Entity)
        root = fromstring(xml_string)
    except ET.ParseError as e:
        logger.error(f"Error al parsear el XML: {e}")
        raise ValueError("El documento XML está mal formado.") from e
    except Exception as e:
        logger.error(f"Error inesperado al procesar el XML: {e}")
        raise ValueError("Error al procesar el documento XML.") from e

    items = []
    for item in root.iter('item'):
        item_data = {
            'value': item.text.strip() if item.text else None,
            'attributes': dict(item.attrib) if item.attrib else None
        }
        items.append(item_data)

    return items
