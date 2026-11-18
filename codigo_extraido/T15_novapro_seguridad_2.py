import os
import tempfile
import uuid

def save_report_to_temp_file(report_data):
    try:
        # Generar un nombre de archivo único para evitar colisiones
        unique_filename = f"report_{uuid.uuid4()}.txt"
        
        # Crear un archivo temporal con un contexto seguro que se cierra automáticamente
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt", prefix="tmp_", dir="/tmp") as temp_file:
            temp_file.write(report_data)
            temp_file_path = temp_file.name
        
        # Verificar que el archivo se ha creado y tiene contenido
        if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
            return temp_file_path
        else:
            raise IOError("El archivo temporal no se creó correctamente o está vacío.")
    
    except Exception as e:
        # Manejar cualquier excepción y asegurar que no se devuelvan rutas inválidas
        print(f"Error al guardar el reporte: {e}")
        return None
