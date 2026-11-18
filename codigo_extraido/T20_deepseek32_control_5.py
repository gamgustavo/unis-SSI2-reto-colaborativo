import os
import zipfile
from pathlib import Path

def extraer_zip(archivo_zip, carpeta_destino='descargas'):
    """
    Extrae el contenido de un archivo ZIP en la carpeta especificada.
    
    Args:
        archivo_zip: Ruta del archivo ZIP a extraer
        carpeta_destino: Carpeta donde se extraerán los archivos (por defecto 'descargas')
    
    Returns:
        str: Ruta completa de la carpeta donde se extrajeron los archivos
    """
    # Crear la ruta completa de la carpeta destino
    carpeta_destino_path = Path(carpeta_destino)
    
    # Crear la carpeta si no existe
    carpeta_destino_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Abrir y extraer el archivo ZIP
        with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
            # Extraer todo el contenido
            zip_ref.extractall(carpeta_destino_path)
            
            # Obtener lista de archivos extraídos
            archivos_extraidos = zip_ref.namelist()
            
            print(f"Archivo ZIP extraído exitosamente en: {carpeta_destino_path.resolve()}")
            print(f"Archivos extraídos: {len(archivos_extraidos)}")
            
            return str(carpeta_destino_path.resolve())
            
    except zipfile.BadZipFile:
        print(f"Error: El archivo '{archivo_zip}' no es un archivo ZIP válido.")
        return None
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo_zip}' no fue encontrado.")
        return None
    except Exception as e:
        print(f"Error al extraer el archivo ZIP: {str(e)}")
        return None

# Ejemplo de uso:
# extraer_zip('archivo_subido.zip')
