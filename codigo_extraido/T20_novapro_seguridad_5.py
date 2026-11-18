import os
import zipfile
from zipfile import ZipFile
from pathlib import Path
import shutil

def extract_zip(uploaded_zip_path, extract_to='descargas'):
    # Asegurarse de que el directorio de extracción existe
    extract_to_path = Path(extract_to)
    extract_to_path.mkdir(parents=True, exist_ok=True)
    
    # Validar que el archivo ZIP esté en un directorio seguro y no contenga rutas relativas peligrosas
    zip_file_path = Path(uploaded_zip_path)
    if not zip_file_path.is_file() or zip_file_path.suffix.lower()!= '.zip':
        raise ValueError("El archivo proporcionado no es un archivo ZIP válido.")
    
    try:
        with ZipFile(zip_file_path, 'r') as zip_ref:
            # Iterar sobre cada miembro del archivo ZIP
            for member in zip_ref.infolist():
                # Comprobar que el nombre del miembro no es una ruta absoluta o contiene '..' para evitar travesías de directorio
                if not member.filename.startswith('..') and '..' not in member.filename.split(os.sep):
                    # Extraer el archivo a la carpeta de destino
                    zip_ref.extract(member, extract_to_path)
                else:
                    raise ValueError(f"El archivo ZIP contiene una ruta no segura: {member.filename}")
    except zipfile.BadZipFile:
        raise ValueError("El archivo ZIP está dañado o es inválido.")
    except Exception as e:
        raise e
    finally:
        # Eliminar el archivo ZIP después de la extracción
        if zip_file_path.exists():
            os.remove(zip_file_path)

# Ejemplo de uso
# extract_zip('ruta/al/archivo.zip')
