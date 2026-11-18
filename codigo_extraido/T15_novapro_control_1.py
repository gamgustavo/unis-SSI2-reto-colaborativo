import tempfile
import os

def guardar_reporte_temporal(datos_reporte):
    try:
        # Crear un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.txt') as temp_file:
            temp_file.write(datos_reporte)
            temp_file.flush()  # Asegurarse de que los datos se escriban en el archivo
            return temp_file.name
    except Exception as e:
        print(f"Ocurrió un error al guardar el reporte: {e}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    datos_reporte = "Este es el contenido del reporte."
    ruta_archivo = guardar_reporte_temporal(datos_reporte)
    if ruta_archivo:
        print(f"El reporte se guardó temporalmente en: {ruta_archivo}")
        # No olvides borrar el archivo temporal cuando ya no sea necesario
        os.remove(ruta_archivo)
        print(f"El archivo temporal en {ruta_archivo} ha sido eliminado.")
