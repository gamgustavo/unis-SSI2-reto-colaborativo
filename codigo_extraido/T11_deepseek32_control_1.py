import xml.etree.ElementTree as ET
from typing import List, Optional

def extract_items_from_xml(xml_content: str) -> List[Optional[str]]:
    """
    Extrae los valores de todos los elementos 'item' de un documento XML.
    
    Args:
        xml_content (str): Cadena con el contenido XML
        
    Returns:
        List[Optional[str]]: Lista con los valores de texto de los elementos 'item'.
                            Retorna lista vacía si no hay elementos 'item' o si hay error.
    """
    try:
        # Parsear el XML
        root = ET.fromstring(xml_content)
        
        # Buscar todos los elementos 'item' en cualquier nivel del árbol
        items = root.findall('.//item')
        
        # Extraer el texto de cada elemento 'item'
        item_values = []
        for item in items:
            # Obtener el texto, si existe
            text = item.text.strip() if item.text and item.text.strip() else None
            item_values.append(text)
        
        return item_values
        
    except ET.ParseError as e:
        print(f"Error al parsear XML: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []

# Ejemplo de uso (comentado):
# xml_data = '''
# <root>
#     <item>Primer elemento</item>
#     <section>
#         <item>Segundo elemento</item>
#         <other>Otro</other>
#     </section>
#     <item>Tercer elemento</item>
# </root>
# '''
# 
# resultado = extract_items_from_xml(xml_data)
# print(resultado)  # ['Primer elemento', 'Segundo elemento', 'Tercer elemento']
