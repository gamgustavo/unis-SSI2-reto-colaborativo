import defusedxml.ElementTree as ET
from typing import List, Dict, Any
import io

def extract_xml_items(xml_content: str) -> List[Dict[str, Any]]:
    """
    Extrae de forma segura los valores de todos los elementos 'item' de un documento XML.
    
    Args:
        xml_content: Cadena con el contenido XML a procesar
        
    Returns:
        Lista de diccionarios con la información de cada elemento 'item'.
        Cada diccionario contiene:
        - 'text': Texto contenido en el elemento (si existe)
        - 'attributes': Atributos del elemento
        - 'children': Subelementos (si existen)
        
    Raises:
        ET.ParseError: Si el XML está mal formado
        ValueError: Si el contenido XML está vacío o es inválido
    """
    if not xml_content or not xml_content.strip():
        raise ValueError("El contenido XML no puede estar vacío")
    
    # Limitar el tamaño del XML para prevenir ataques DoS
    max_xml_size = 10 * 1024 * 1024  # 10 MB
    if len(xml_content.encode('utf-8')) > max_xml_size:
        raise ValueError(f"El tamaño del XML excede el límite de {max_xml_size // (1024*1024)} MB")
    
    items_data = []
    
    try:
        # Usar defusedxml para prevenir ataques XML External Entity (XXE)
        # y otros ataques relacionados con XML
        root = ET.fromstring(xml_content)
        
        # Buscar todos los elementos 'item' en el documento
        for item in root.iter('item'):
            item_data = {
                'text': item.text.strip() if item.text and item.text.strip() else None,
                'attributes': dict(item.attrib),
                'children': []
            }
            
            # Procesar subelementos si existen
            for child in item:
                child_data = {
                    'tag': child.tag,
                    'text': child.text.strip() if child.text and child.text.strip() else None,
                    'attributes': dict(child.attrib)
                }
                item_data['children'].append(child_data)
            
            items_data.append(item_data)
            
    except ET.ParseError as e:
        raise ET.ParseError(f"Error al parsear XML: {str(e)}")
    except Exception as e:
        # Log genérico para capturar otros errores inesperados
        raise RuntimeError(f"Error procesando XML: {str(e)}")
    
    return items_data


def safe_extract_items_from_xml(xml_content: str) -> List[str]:
    """
    Versión simplificada que extrae solo el texto de los elementos 'item'.
    Más segura para casos donde solo se necesita el texto.
    
    Args:
        xml_content: Cadena con el contenido XML
        
    Returns:
        Lista con el texto de cada elemento 'item' encontrado
    """
    if not xml_content or not xml_content.strip():
        return []
    
    # Validación básica de entrada
    if len(xml_content) > 10 * 1024 * 1024:  # 10 MB
        return []
    
    items_text = []
    
    try:
        # Usar defusedxml con parser restringido
        parser = ET.DefusedXMLParser(
            forbid_dtd=True,          # Prevenir DTD
            forbid_entities=True,     # Prevenir entidades externas
            forbid_external=True      # Prevenir recursos externos
        )
        
        root = ET.fromstring(xml_content, parser=parser)
        
        # Extraer solo el texto de los elementos 'item'
        for item in root.iter('item'):
            if item.text and item.text.strip():
                # Limpiar y normalizar el texto
                text = item.text.strip()
                # Limitar longitud del texto extraído
                if len(text) > 10000:  # Límite de 10k caracteres por item
                    text = text[:10000] + "... [TRUNCADO]"
                items_text.append(text)
                
    except (ET.ParseError, ValueError, TypeError):
        # En caso de error, retornar lista vacía
        return []
    except Exception:
        # Capturar cualquier otro error inesperado
        return []
    
    return items_text


# Ejemplo de uso:
if __name__ == "__main__":
    # XML de ejemplo para pruebas
    sample_xml = """<?xml version="1.0"?>
    <catalog>
        <item id="1">
            <name>Producto A</name>
            <price>100</price>
        </item>
        <item id="2">
            <name>Producto B</name>
            <price>200</price>
        </item>
        <other>No es un item</other>
    </catalog>"""
    
    try:
        # Usar la función principal
        items = extract_xml_items(sample_xml)
        print(f"Se encontraron {len(items)} elementos 'item'")
        
        # O usar la versión simplificada
        texts = safe_extract_items_from_xml(sample_xml)
        print(f"Textos extraídos: {texts}")
        
    except Exception as e:
        print(f"Error: {e}")
