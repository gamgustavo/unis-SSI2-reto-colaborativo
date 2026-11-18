import defusedxml.ElementTree as ET
from typing import List, Dict, Any
import io

def extract_items_from_xml(xml_content: str) -> List[Dict[str, Any]]:
    """
    Extrae los valores de todos los elementos 'item' de un documento XML.
    
    Args:
        xml_content: Cadena con el contenido XML a procesar
        
    Returns:
        Lista de diccionarios con la información de cada elemento 'item'.
        Cada diccionario contiene:
        - 'text': Texto contenido en el elemento (si existe)
        - 'attributes': Atributos del elemento
        - 'children': Elementos hijos (si existen)
        
    Raises:
        ET.ParseError: Si el XML está mal formado
        ValueError: Si el contenido XML está vacío o es inválido
    """
    if not xml_content or not xml_content.strip():
        raise ValueError("El contenido XML no puede estar vacío")
    
    # Limitar el tamaño del XML para prevenir ataques de DoS
    max_xml_size = 10 * 1024 * 1024  # 10 MB
    if len(xml_content.encode('utf-8')) > max_xml_size:
        raise ValueError(f"El tamaño del XML excede el límite de {max_xml_size // (1024*1024)} MB")
    
    items = []
    
    try:
        # Usar defusedxml para prevenir ataques XML External Entity (XXE)
        # y otros ataques relacionados con XML
        root = ET.fromstring(xml_content)
        
        # Buscar todos los elementos 'item' en el documento
        for item_element in root.iter('item'):
            item_data = {
                'text': item_element.text.strip() if item_element.text else None,
                'attributes': dict(item_element.attrib),
                'children': []
            }
            
            # Procesar elementos hijos
            for child in item_element:
                child_data = {
                    'tag': child.tag,
                    'text': child.text.strip() if child.text else None,
                    'attributes': dict(child.attrib)
                }
                item_data['children'].append(child_data)
            
            items.append(item_data)
            
    except ET.ParseError as e:
        raise ET.ParseError(f"Error al parsear XML: {str(e)}")
    except Exception as e:
        # Log genérico para errores inesperados (en producción usar logging)
        raise RuntimeError(f"Error inesperado al procesar XML: {str(e)}")
    
    return items


def safe_extract_items(xml_content: str) -> List[Dict[str, Any]]:
    """
    Versión segura de extract_items_from_xml con manejo adicional de errores.
    
    Args:
        xml_content: Cadena con el contenido XML a procesar
        
    Returns:
        Lista de diccionarios con la información de cada elemento 'item'.
        Lista vacía si no hay elementos 'item' o si ocurre un error.
    """
    try:
        # Validación adicional del input
        if not isinstance(xml_content, str):
            raise TypeError("El contenido XML debe ser una cadena de texto")
        
        # Limpieza básica del input (eliminar caracteres nulos)
        xml_content = xml_content.replace('\x00', '')
        
        return extract_items_from_xml(xml_content)
        
    except (ET.ParseError, ValueError, TypeError, RuntimeError) as e:
        # En producción, aquí se debería registrar el error
        print(f"Error seguro al procesar XML: {str(e)}")
        return []
    except Exception as e:
        # Capturar cualquier otro error inesperado
        print(f"Error inesperado: {str(e)}")
        return []


# Ejemplo de uso:
if __name__ == "__main__":
    # XML de ejemplo para pruebas
    sample_xml = """<?xml version="1.0"?>
    <catalog>
        <item id="1">
            <name>Producto A</name>
            <price>100.00</price>
        </item>
        <item id="2">
            <name>Producto B</name>
            <price>200.00</price>
        </item>
        <other>No es un item</other>
    </catalog>"""
    
    try:
        items = safe_extract_items(sample_xml)
        print(f"Se encontraron {len(items)} elementos 'item':")
        for i, item in enumerate(items, 1):
            print(f"\nItem {i}:")
            print(f"  Texto: {item['text']}")
            print(f"  Atributos: {item['attributes']}")
            print(f"  Hijos: {len(item['children'])}")
            for child in item['children']:
                print(f"    - {child['tag']}: {child['text']}")
    except Exception as e:
        print(f"Error: {e}")
