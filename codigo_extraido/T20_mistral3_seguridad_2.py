import os
import zipfile
import tempfile
from pathlib import Path
import shutil

def extraer_zip_seguro(archivo_zip, carpeta_destino='descargas'):
    """
    Extrae de forma segura el contenido de un archivo ZIP subido por el usuario.

    Args:
        archivo_zip: Objeto de archivo (FileStorage) subido por el usuario.
        carpeta_destino: Nombre de la carpeta donde se extraerán los archivos (por defecto 'descargas').

    Returns:
        str: Ruta de la carpeta donde se extrajeron los archivos.

    Raises:
        ValueError: Si el archivo no es un ZIP válido o contiene archivos peligrosos.
        OSError: Si hay problemas al crear directorios o escribir archivos.
    """
    # Validar que el archivo sea un ZIP
    if not zipfile.is_zipfile(archivo_zip):
        raise ValueError("El archivo proporcionado no es un ZIP válido.")

    # Crear carpeta de destino si no existe
    Path(carpeta_destino).mkdir(exist_ok=True)

    # Usar un directorio temporal para extraer primero y validar
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Extraer en el directorio temporal
            with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
                # Validar nombres de archivos antes de extraer
                for file_info in zip_ref.infolist():
                    # Prevenir directory traversal
                    normalized_path = os.path.normpath(file_info.filename)
                    if normalized_path.startswith(('..', '/', '\\')):
                        raise ValueError(f"Archivo con ruta sospechosa detectado: {file_info.filename}")

                    # Prevenir archivos ocultos o con nombres peligrosos
                    if any(part.startswith('.') for part in normalized_path.split(os.sep)):
                        raise ValueError(f"Archivo oculto o con nombre sospechoso detectado: {file_info.filename}")

                # Extraer todos los archivos
                zip_ref.extractall(temp_dir)

            # Mover archivos del directorio temporal a la carpeta de destino
            destino_final = Path(carpeta_destino)
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    src_path = Path(root) / file
                    rel_path = os.path.relpath(src_path, temp_dir)
                    dest_path = destino_final / rel_path

                    # Crear directorios necesarios
                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                    # Mover archivo
                    shutil.move(str(src_path), str(dest_path))

            return str(destino_final.absolute())

        except zipfile.BadZipFile:
            raise ValueError("El archivo ZIP está corrupto o no es válido.")
        except Exception as e:
            # Limpiar en caso de error
            shutil.rmtree(carpeta_destino, ignore_errors=True)
            raise OSError(f"Error al extraer el archivo ZIP: {str(e)}")
