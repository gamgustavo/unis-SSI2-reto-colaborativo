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
        str: Ruta de la carpeta donde se extrajeron los archivos
    """
    # Crear la carpeta de destino si no existe
    carpeta_destino = Path(carpeta_destino)
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    
    try:
        # Abrir y extraer el archivo ZIP
        with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
            # Extraer todo el contenido
            zip_ref.extractall(carpeta_destino)
            
            # Obtener lista de archivos extraídos
            archivos_extraidos = zip_ref.namelist()
            
            print(f"Archivo ZIP extraído exitosamente en: {carpeta_destino.absolute()}")
            print(f"Archivos extraídos: {len(archivos_extraidos)}")
            
            return str(carpeta_destino.absolute())
            
    except zipfile.BadZipFile:
        raise ValueError("El archivo no es un ZIP válido o está corrupto")
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {archivo_zip}")
    except Exception as e:
        raise Exception(f"Error al extraer el archivo ZIP: {str(e)}")

# Ejemplo de uso (comentado):
# if __name__ == "__main__":
#     # Para usar con un archivo subido por el usuario
#     ruta_zip = "archivo_subido.zip"  # Reemplazar con la ruta real del archivo
#     try:
#         resultado = extraer_zip(ruta_zip)
#         print(f"Contenido extraído en: {resultado}")
#     except Exception as e:
#         print(f"Error: {e}")
