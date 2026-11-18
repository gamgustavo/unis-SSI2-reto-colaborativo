import os
import tempfile
import uuid

def save_report_to_temp_file(report_data):
    if not isinstance(report_data, str):
        raise ValueError("report_data debe ser una cadena")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.txt') as temp_file:
            unique_id = uuid.uuid4()
            temp_file.write(report_data)
            temp_file_path = f"{temp_file.name}.{unique_id}.txt"
            os.rename(temp_file.name, temp_file_path)
            return temp_file_path
    except Exception as e:
        raise RuntimeError(f"Error al guardar el reporte: {e}")

# Ejemplo de uso
# report_data = "Este es el contenido del reporte."
# file_path = save_report_to_temp_file(report_data)
# print(f"Reporte guardado en: {file_path}")
