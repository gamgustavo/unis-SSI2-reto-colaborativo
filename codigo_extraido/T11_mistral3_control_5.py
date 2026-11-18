import xml.etree.ElementTree as ET

def extraer_items_xml(xml_string):
    """
    Extrae los valores de todos los elementos 'item' en un documento XML.

    Args:
        xml_string (str): Cadena que contiene el documento XML.

    Returns:
        list: Lista con los valores de los elementos 'item'.
    """
    try:
        root = ET.fromstring(xml_string)
        items = [item.text for item in root.findall('.//item')]
        return items
    except ET.ParseError as e:
        print(f"Error al parsear el XML: {e}")
        return []
