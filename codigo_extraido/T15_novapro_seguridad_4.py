import os
import tempfile
import shutil

def save_report_to_temp(report_data, prefix="report", suffix=".txt"):
    try:
        # Crear un archivo temporal seguro
        with tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix) as temp_file:
            temp_file.write(report_data.encode('utf-8'))
            temp_file_path = temp_file.name
        
        # Asegurarse de que el archivo temporal tiene permisos restringidos
        os.chmod(temp_file_path, 0o600)
        
        return temp_file_path
    
    except Exception as e:
        # Manejar cualquier excepción y eliminar el archivo temporal si se produce un error
        if 'temp_file_path' in locals():
            os.remove(temp_file_path)
        raise RuntimeError(f"Error al guardar el reporte: {e}")

def secure_delete_temp_file(file_path):
    try:
        # Eliminar el archivo temporal de forma segura
        if os.path.exists(file_path):
            shutil.rmtree(file_path, ignore_errors=True)
    except Exception as e:
        raise RuntimeError(f"Error al eliminar el archivo temporal: {e}")
