import os
import tempfile
import uuid

def save_report_to_temp(report_data):
    try:
        # Generar un nombre de archivo único para evitar colisiones
        unique_filename = f"report_{uuid.uuid4()}.txt"
        
        # Crear un archivo temporal con eliminación segura al cerrar
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt") as temp_file:
            temp_file.write(report_data)
            temp_file_path = temp_file.name
        
        # Asegurarse de que el archivo tiene permisos de lectura y escritura solo para el propietario
        os.chmod(temp_file_path, 0o600)
        
        return temp_file_path
    
    except Exception as e:
        # Manejar cualquier excepción y asegurar que no se devuelva información sensible
        print(f"Error al guardar el reporte: {e}")
        return None
