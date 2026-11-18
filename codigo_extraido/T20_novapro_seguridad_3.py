import os
import zipfile
from zipfile import ZipFile
from pathlib import Path
from tempfile import TemporaryDirectory

def extract_zip(uploaded_zip_path):
    downloads_folder = Path('descargas')
    downloads_folder.mkdir(exist_ok=True)
    
    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        try:
            with ZipFile(uploaded_zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir_path)
                
                for item in temp_dir_path.iterdir():
                    if item.is_dir():
                        for sub_item in item.iterdir():
                            if sub_item.is_file():
                                sub_item.replace(downloads_folder / sub_item.name)
                    else:
                        item.replace(downloads_folder / item.name)
                        
            return "Archivos extraídos con éxito."
        
        except zipfile.BadZipFile:
            return "El archivo ZIP está dañado o es inválido."
        except Exception as e:
            return f"Ocurrió un error al extraer el archivo: {e}"

# Ejemplo de uso
# uploaded_zip_path = 'ruta/al/archivo.zip'
# print(extract_zip(uploaded_zip_path))
