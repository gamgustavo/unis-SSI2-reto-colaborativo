import xml.etree.ElementTree as ET
from defusedxml.ElementTree import fromstring
from typing import List, Dict, Optional
import logging

# Configuración básica de logging para registrar errores
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def extract_items_from_xml(xml_string: str) -> List[Dict[str, Optional[str]]]:
    """
    Extrae los valores de todos los elementos 'item' de un documento XML.

    Args:
        xml_string: Cadena que contiene el documento XML.

    Returns:
        Lista de diccionarios con los valores de los elementos 'item' y sus atributos.
        Cada diccionario contiene:
        - 'text': Texto del elemento (None si no tiene texto)
        - 'attributes': Diccionario de atributos (vacío si no tiene atributos)
        - 'children': Lista de hijos (cada hijo es un diccionario similar)

    Raises:
        ValueError: Si el XML está mal formado o contiene entidades externas peligrosas.
        ET.ParseError: Si hay errores al parsear el XML.
    """
    if not xml_string or not isinstance(xml_string, str):
        logger.error("Input XML is empty or not a string")
        raise ValueError("Input XML must be a non-empty string")

    try:
        # Usamos defusedxml para prevenir ataques XXE (XML External Entity)
        root = fromstring(xml_string)
    except ET.ParseError as e:
        logger.error(f"XML parsing error: {str(e)}")
        raise ValueError("Invalid XML format") from e
    except Exception as e:
        logger.error(f"Unexpected error parsing XML: {str(e)}")
        raise ValueError("Error processing XML") from e

    items = []

    for item in root.findall('.//item'):
        try:
            item_data = {
                'text': item.text.strip() if item.text else None,
                'attributes': dict(item.attrib),
                'children': []
            }

            # Procesar hijos recursivamente
            for child in item:
                child_data = {
                    'tag': child.tag,
                    'text': child.text.strip() if child.text else None,
                    'attributes': dict(child.attrib),
                    'children': []
                }

                # Procesar nietos (evitamos recursión infinita con un límite)
                for grandchild in child:
                    grandchild_data = {
                        'tag': grandchild.tag,
                        'text': grandchild.text.strip() if grandchild.text else None,
                        'attributes': dict(grandchild.attrib),
                        'children': []  # No procesamos más niveles por seguridad
                    }
                    child_data['children'].append(grandchild_data)

                item_data['children'].append(child_data)

            items.append(item_data)
        except Exception as e:
            logger.error(f"Error processing item: {str(e)}")
            continue  # Continuamos con el siguiente item aunque uno falle

    return items
