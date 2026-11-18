import defusedxml.ElementTree as ET
from typing import List, Dict, Any
import io

def extract_xml_items(xml_content: str) -> List[Dict[str, Any]]:
    """
    Extrae los valores de todos los elementos 'item' de un documento XML.
    
    Args:
        xml_content (str): Contenido XML como string
        
    Returns:
        List[Dict[str, Any]]: Lista de diccionarios con la información de cada item.
                              Cada diccionario contiene los atributos y texto del elemento.
                              
    Raises:
        ET.ParseError: Si el XML está mal formado
        ValueError: Si el contenido XML está vacío o es inválido
    """
    
    # Validación básica de entrada
    if not xml_content or not xml_content.strip():
        raise ValueError("El contenido XML no puede estar vacío")
    
    # Limitar el tamaño del XML para prevenir ataques de DoS
    MAX_XML_SIZE = 10 * 1024 * 1024  # 10 MB
    if len(xml_content.encode('utf-8')) > MAX_XML_SIZE:
        raise ValueError(f"El tamaño del XML excede el límite de {MAX_XML_SIZE // (1024*1024)} MB")
    
    items = []
    
    try:
        # Usar defusedxml para prevenir ataques XML (XXE, bombas XML, etc.)
        # Parsear desde string con defusedxml
        root = ET.fromstring(xml_content)
        
        # Buscar todos los elementos 'item' en el documento
        # Usar namespaces si están presentes
        namespaces = {}
        if '}' in root.tag:
            # Extraer namespace si existe
            namespace = root.tag.split('}')[0].strip('{')
            namespaces['ns'] = namespace
        
        # Buscar elementos 'item' considerando namespaces
        item_elements = root.findall('.//item') if not namespaces else root.findall('.//ns:item', namespaces)
        
        for item in item_elements:
            item_data = {
                'text': item.text.strip() if item.text else None,
                'attributes': dict(item.attrib),
                'children': {}
            }
            
            # Extraer información de elementos hijos
            for child in item:
                # Usar el nombre del tag sin namespace si existe
                tag_name = child.tag
                if '}' in tag_name:
                    tag_name = tag_name.split('}')[1]
                
                child_text = child.text.strip() if child.text else None
                if child_text:
                    item_data['children'][tag_name] = child_text
            
            items.append(item_data)
            
    except ET.ParseError as e:
        # Registrar el error sin exponer detalles internos
        raise ET.ParseError(f"Error al parsear XML: {str(e)}")
    except Exception as e:
        # Capturar cualquier otra excepción y convertirla en algo seguro
        raise ValueError(f"Error procesando XML: {str(e)}")
    
    return items


def safe_extract_items_from_file(xml_file_path: str) -> List[Dict[str, Any]]:
    """
    Versión segura para extraer items desde un archivo XML.
    
    Args:
        xml_file_path (str): Ruta al archivo XML
        
    Returns:
        List[Dict[str, Any]]: Lista de diccionarios con la información de cada item.
    """
    try:
        # Validar extensión del archivo
        if not xml_file_path.lower().endswith('.xml'):
            raise ValueError("El archivo debe tener extensión .xml")
        
        # Leer con límite de tamaño
        with open(xml_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read(MAX_XML_SIZE + 1)
            if len(content) > MAX_XML_SIZE:
                raise ValueError(f"Archivo XML demasiado grande (límite: {MAX_XML_SIZE // (1024*1024)} MB)")
        
        return extract_xml_items(content)
        
    except FileNotFoundError:
        raise ValueError("Archivo no encontrado")
    except PermissionError:
        raise ValueError("Permiso denegado para leer el archivo")
    except IOError as e:
        raise ValueError(f"Error de E/S al leer el archivo: {str(e)}")


# Ejemplo de uso (comentado para evitar ejecución accidental):
"""
# Uso desde string XML
xml_string = '''<?xml version="1.0"?>
<catalog>
    <item id="1">
        <name>Producto A</name>
        <price>100</price>
    </item>
    <item id="2">
        <name>Producto B</name>
        <price>200</price>
    </item>
</catalog>'''

try:
    items = extract_xml_items(xml_string)
    for item in items:
        print(f"Item: {item}")
except Exception as e:
    print(f"Error: {e}")

# Uso desde archivo
# try:
#     items = safe_extract_items_from_file("documento.xml")
# except Exception as e:
#     print(f"Error: {e}")
"""
