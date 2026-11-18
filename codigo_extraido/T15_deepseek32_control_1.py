import tempfile
import os
import json

def guardar_reporte_temporal(datos_reporte, formato='txt'):
    """
    Guarda datos de un reporte en un archivo temporal y devuelve la ruta.
    
    Args:
        datos_reporte: Datos a guardar (pueden ser string, dict, list, etc.)
        formato: Formato del archivo ('txt', 'json', 'csv', etc.)
    
    Returns:
        str: Ruta completa del archivo temporal creado
    """
    # Crear un archivo temporal con el sufijo adecuado
    sufijo = f'.{formato}' if not formato.startswith('.') else formato
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=sufijo) as temp_file:
        
        # Escribir los datos según su tipo y formato
        if isinstance(datos_reporte, (dict, list)) and formato in ['json', '.json']:
            json.dump(datos_reporte, temp_file, indent=2)
        elif isinstance(datos_reporte, str):
            temp_file.write(datos_reporte)
        else:
            # Convertir a string para otros tipos de datos
            temp_file.write(str(datos_reporte))
        
        ruta_archivo = temp_file.name
    
    return ruta_archivo

# Ejemplo de uso:
if __name__ == "__main__":
    # Ejemplo 1: Datos en formato texto
    datos_texto = "Reporte de ventas\nProducto A: 100 unidades\nProducto B: 150 unidades"
    ruta1 = guardar_reporte_temporal(datos_texto, 'txt')
    print(f"Archivo creado: {ruta1}")
    
    # Ejemplo 2: Datos en formato JSON
    datos_json = {
        "reporte": "ventas",
        "fecha": "2024-01-15",
        "ventas": [100, 150, 200]
    }
    ruta2 = guardar_reporte_temporal(datos_json, 'json')
    print(f"Archivo creado: {ruta2}")
    
    # Limpiar archivos temporales (opcional)
    os.unlink(ruta1)
    os.unlink(ruta2)
