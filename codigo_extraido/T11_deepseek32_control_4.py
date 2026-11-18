import xml.etree.ElementTree as ET
from typing import List, Optional

def extract_items_from_xml(xml_content: str) -> List[Optional[str]]:
    """
    Extrae los valores de todos los elementos 'item' de un documento XML.
    
    Args:
        xml_content (str): Cadena con el contenido XML a procesar.
    
    Returns:
        List[Optional[str]]: Lista con los valores de texto de los elementos 'item'.
                             Retorna lista vacía si no hay elementos 'item' o si hay error.
    """
    try:
        # Parsear el XML
        root = ET.fromstring(xml_content)
        
        # Buscar todos los elementos 'item' en cualquier nivel del documento
        items = root.findall('.//item')
        
        # Extraer el texto de cada elemento 'item'
        # Si un elemento no tiene texto, se guarda como None
        item_values = [item.text for item in items]
        
        return item_values
        
    except ET.ParseError as e:
        print(f"Error al parsear XML: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []

# Ejemplo de uso (comentado):
# xml_data = '''<?xml version="1.0"?>
# <catalog>
#     <item>Manzanas</item>
#     <item>Naranjas</item>
#     <category>
#         <item>Plátanos</item>
#     </category>
# </catalog>'''
# 
# resultado = extract_items_from_xml(xml_data)
# print(resultado)  # ['Manzanas', 'Naranjas', 'Plátanos']
