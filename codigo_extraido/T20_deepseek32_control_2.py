import os
import zipfile
import shutil
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
    try:
        # Crear la carpeta de destino si no existe
        carpeta_destino = Path(carpeta_destino)
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        # Verificar que el archivo ZIP existe
        if not os.path.exists(archivo_zip):
            raise FileNotFoundError(f"El archivo {archivo_zip} no existe")
        
        # Verificar que es un archivo ZIP válido
        if not zipfile.is_zipfile(archivo_zip):
            raise ValueError(f"El archivo {archivo_zip} no es un ZIP válido")
        
        # Extraer el contenido del ZIP
        with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
            # Obtener el nombre base del archivo ZIP (sin extensión)
            nombre_base = Path(archivo_zip).stem
            
            # Crear una subcarpeta con el nombre del ZIP para evitar conflictos
            carpeta_extraccion = carpeta_destino / nombre_base
            carpeta_extraccion.mkdir(exist_ok=True)
            
            # Extraer todos los archivos
            zip_ref.extractall(carpeta_extraccion)
            
            print(f"Archivos extraídos exitosamente en: {carpeta_extraccion}")
            print(f"Total de archivos extraídos: {len(zip_ref.namelist())}")
            
            return str(carpeta_extraccion)
            
    except zipfile.BadZipFile:
        raise ValueError(f"El archivo {archivo_zip} está corrupto o no es un ZIP válido")
    except PermissionError:
        raise PermissionError(f"No se tienen permisos para escribir en {carpeta_destino}")
    except Exception as e:
        raise Exception(f"Error al extraer el archivo ZIP: {str(e)}")

# Ejemplo de uso (comentado):
# if __name__ == "__main__":
#     # Para usar con un archivo subido por el usuario
#     ruta_zip = "ruta/al/archivo.zip"  # Reemplazar con la ruta real
#     try:
#         resultado = extraer_zip(ruta_zip)
#         print(f"Extracción completada: {resultado}")
#     except Exception as e:
#         print(f"Error: {e}")
