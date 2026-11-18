import xml.etree.ElementTree as ET

def extract_item_values(xml_document):
    try:
        # Parsear el documento XML
        root = ET.fromstring(xml_document)
        
        # Verificar si el documento XML es válido
        if root is None:
            raise ET.ParseError("El documento XML no es válido.")
        
        # Encontrar todos los elementos 'item' y extraer sus valores
        item_values = []
        for item in root.findall('.//item'):
            if item.text:
                item_values.append(item.text.strip())
        
        return item_values
    
    except ET.ParseError as e:
        print(f"Error al parsear el documento XML: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []

# Ejemplo de uso
xml_doc = """
<root>
    <item>Valor1</item>
    <item>Valor2</item>
    <other>NoItem</other>
    <item>Valor3</item>
</root>
"""
print(extract_item_values(xml_doc))
