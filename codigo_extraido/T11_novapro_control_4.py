from xml.etree import ElementTree as ET

def extraer_items(xml_documento):
    try:
        # Parsear el documento XML
        root = ET.fromstring(xml_documento)
        
        # Encontrar todos los elementos 'item'
        items = root.findall('.//item')
        
        # Extraer los valores de los elementos 'item'
        valores_items = [item.text for item in items if item.text is not None]
        
        return valores_items
    except ET.ParseError:
        return "Error: El documento XML no es válido."

# Ejemplo de uso
xml_documento = '''
<root>
    <item>Valor1</item>
    <otro_elemento>
        <item>Valor2</item>
    </otro_elemento>
    <item>Valor3</item>
</root>
'''
print(extraer_items(xml_documento))
