import os
import zipfile
from werkzeug.utils import secure_filename

def extraer_zip(archivo_zip, carpeta_destino='descargas'):
    # Crear la carpeta de destino si no existe
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    # Guardar el archivo ZIP temporalmente
    nombre_seguro = secure_filename(archivo_zip.filename)
    ruta_temporal = os.path.join(carpeta_destino, nombre_seguro)
    archivo_zip.save(ruta_temporal)

    # Extraer el contenido del ZIP
    with zipfile.ZipFile(ruta_temporal, 'r') as zip_ref:
        zip_ref.extractall(carpeta_destino)

    # Eliminar el archivo ZIP temporal
    os.remove(ruta_temporal)

    return f"Archivo extraído en {os.path.abspath(carpeta_destino)}"
