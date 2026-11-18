import xml.etree.ElementTree as ET

def extract_item_values(xml_document):
    try:
        # Parsear el documento XML
        root = ET.fromstring(xml_document)
        
        # Verificar si el documento XML es válido
        if root is None:
            return []

        # Extraer los valores de todos los elementos 'item'
        item_values = []
        for item in root.findall('.//item'):
            if item.text:
                item_values.append(item.text.strip())
        
        return item_values
    
    except ET.ParseError:
        # Manejar errores de parsing XML
        return []

# Ejemplo de uso
# xml_document = '<root><item>Valor1</item><item>Valor2</item></root>'
# print(extract_item_values(xml_document))
