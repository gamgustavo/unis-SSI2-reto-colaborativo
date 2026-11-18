import xml.etree.ElementTree as ET
from typing import List, Optional

def extract_items_from_xml(xml_content: str) -> List[Optional[str]]:
    """
    Extrae los valores de todos los elementos 'item' en un documento XML.
    
    Args:
        xml_content (str): Cadena con el contenido XML a procesar.
    
    Returns:
        List[Optional[str]]: Lista con los valores de texto de los elementos 'item'.
                             Retorna lista vacía si no hay elementos 'item' o si hay error.
    """
    items = []
    
    try:
        # Parsear el contenido XML
        root = ET.fromstring(xml_content)
        
        # Buscar todos los elementos 'item' en todo el documento
        # Usamos iter para encontrar elementos en cualquier nivel
        for item_element in root.iter('item'):
            # Obtener el texto del elemento (puede ser None si el elemento está vacío)
            item_text = item_element.text
            items.append(item_text)
            
    except ET.ParseError as e:
        print(f"Error al parsear XML: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []
    
    return items

# Ejemplo de uso (comentado):
# if __name__ == "__main__":
#     xml_ejemplo = '''
#     <root>
#         <item>Primer elemento</item>
#         <section>
#             <item>Segundo elemento</item>
#             <subitem>
#                 <item>Tercer elemento</item>
#             </subitem>
#         </section>
#         <item></item>
#         <item>Cuarto elemento</item>
#     </root>
#     '''
#     
#     resultados = extract_items_from_xml(xml_ejemplo)
#     print("Elementos 'item' encontrados:")
#     for i, item in enumerate(resultados, 1):
#         print(f"{i}: {item}")
