import tempfile
import os
import json

def guardar_reporte_temporal(datos_reporte, formato='txt'):
    """
    Guarda datos de un reporte en un archivo temporal y devuelve la ruta del archivo.
    
    Args:
        datos_reporte: Datos a guardar (pueden ser string, diccionario, lista, etc.)
        formato: Formato del archivo ('txt', 'json', 'csv', etc.)
    
    Returns:
        str: Ruta completa del archivo temporal creado
    """
    # Crear un archivo temporal con el formato especificado
    with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{formato}', delete=False) as temp_file:
        # Determinar cómo escribir los datos según el tipo y formato
        if formato == 'json' and isinstance(datos_reporte, (dict, list)):
            json.dump(datos_reporte, temp_file, indent=2)
        elif formato == 'csv' and isinstance(datos_reporte, list):
            # Para CSV simple (asumiendo lista de listas o lista de diccionarios)
            import csv
            if datos_reporte and isinstance(datos_reporte[0], dict):
                writer = csv.DictWriter(temp_file, fieldnames=datos_reporte[0].keys())
                writer.writeheader()
                writer.writerows(datos_reporte)
            else:
                writer = csv.writer(temp_file)
                writer.writerows(datos_reporte)
        else:
            # Para texto plano o cualquier otro formato
            temp_file.write(str(datos_reporte))
        
        ruta_archivo = temp_file.name
    
    return ruta_archivo
