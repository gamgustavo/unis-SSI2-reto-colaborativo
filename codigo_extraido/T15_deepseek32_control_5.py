import tempfile
import os
import json

def guardar_reporte_temporal(datos_reporte, nombre_archivo=None, formato='json'):
    """
    Guarda datos de un reporte en un archivo temporal y devuelve la ruta del archivo.
    
    Args:
        datos_reporte: Los datos del reporte a guardar (pueden ser dict, list, str, etc.)
        nombre_archivo: Nombre base para el archivo (opcional)
        formato: Formato del archivo ('json', 'txt', 'csv', etc.)
    
    Returns:
        str: Ruta completa del archivo temporal creado
    """
    try:
        # Crear un archivo temporal con el nombre y formato especificados
        if nombre_archivo:
            # Si se proporciona un nombre, crear un archivo temporal con ese nombre
            sufijo = f'.{formato}' if not nombre_archivo.endswith(f'.{formato}') else ''
            archivo_temp = tempfile.NamedTemporaryFile(
                mode='w',
                prefix=nombre_archivo.replace(f'.{formato}', '') + '_',
                suffix=sufijo,
                delete=False
            )
        else:
            # Si no se proporciona nombre, crear un archivo temporal genérico
            sufijo = f'.{formato}'
            archivo_temp = tempfile.NamedTemporaryFile(
                mode='w',
                suffix=sufijo,
                delete=False
            )
        
        # Escribir los datos en el archivo según el formato
        if formato == 'json':
            # Si los datos son un string, intentar cargarlos como JSON primero
            if isinstance(datos_reporte, str):
                try:
                    datos = json.loads(datos_reporte)
                    json.dump(datos, archivo_temp, indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    # Si no es JSON válido, guardar como texto plano
                    archivo_temp.write(datos_reporte)
            else:
                # Si no es string, asumir que es serializable a JSON
                json.dump(datos_reporte, archivo_temp, indent=2, ensure_ascii=False)
        
        elif formato == 'txt':
            archivo_temp.write(str(datos_reporte))
        
        elif formato == 'csv':
            # Manejo básico de datos CSV
            if isinstance(datos_reporte, list):
                import csv
                writer = csv.writer(archivo_temp)
                writer.writerows(datos_reporte)
            elif isinstance(datos_reporte, str):
                archivo_temp.write(datos_reporte)
            else:
                archivo_temp.write(str(datos_reporte))
        
        else:
            # Para otros formatos, guardar como texto
            archivo_temp.write(str(datos_reporte))
        
        archivo_temp.close()
        return archivo_temp.name
        
    except Exception as e:
        # En caso de error, limpiar cualquier archivo temporal creado
        if 'archivo_temp' in locals() and os.path.exists(archivo_temp.name):
            os.unlink(archivo_temp.name)
        raise Exception(f"Error al guardar el reporte temporal: {str(e)}")
