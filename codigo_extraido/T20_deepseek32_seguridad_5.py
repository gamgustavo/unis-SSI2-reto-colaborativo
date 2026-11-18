import os
import zipfile
import tempfile
import shutil
import pathlib
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_zip_safely(zip_file_path: str, extract_to: str = 'descargas') -> Optional[str]:
    """
    Extrae de forma segura un archivo ZIP en el directorio especificado.
    
    Args:
        zip_file_path: Ruta al archivo ZIP
        extract_to: Directorio de destino (por defecto 'descargas')
    
    Returns:
        str: Ruta del directorio de extracción si es exitoso, None si hay error
    
    Raises:
        ValueError: Si el archivo ZIP no es válido o hay problemas de seguridad
    """
    
    # Validaciones iniciales
    if not os.path.exists(zip_file_path):
        logger.error(f"El archivo no existe: {zip_file_path}")
        return None
    
    if not zipfile.is_zipfile(zip_file_path):
        logger.error(f"El archivo no es un ZIP válido: {zip_file_path}")
        return None
    
    # Crear directorio de descargas si no existe
    download_dir = os.path.abspath(extract_to)
    os.makedirs(download_dir, exist_ok=True)
    
    # Crear directorio temporal para extracción segura
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Validar cada archivo en el ZIP antes de extraer
                for file_info in zip_ref.infolist():
                    # Normalizar la ruta del archivo
                    normalized_path = os.path.normpath(file_info.filename)
                    
                    # Verificar que no sea una ruta absoluta
                    if os.path.isabs(normalized_path):
                        raise ValueError(f"Ruta absoluta no permitida: {normalized_path}")
                    
                    # Verificar que no contenga secuencias peligrosas
                    dangerous_patterns = ['..', '~', '/etc/', '/bin/', '/usr/', 'C:\\', 'COM', 'LPT']
                    for pattern in dangerous_patterns:
                        if pattern in normalized_path:
                            raise ValueError(f"Ruta contiene patrón peligroso: {normalized_path}")
                    
                    # Verificar que no sea un enlace simbólico (ZipBomb protection)
                    if file_info.external_attr and (file_info.external_attr >> 28) == 0xA:
                        raise ValueError(f"Enlace simbólico detectado: {normalized_path}")
                    
                    # Verificar tamaño del archivo (límite de 1GB por archivo)
                    if file_info.file_size > 1024 * 1024 * 1024:
                        raise ValueError(f"Archivo demasiado grande: {normalized_path}")
                
                # Extraer primero al directorio temporal
                zip_ref.extractall(temp_dir)
                
                # Verificar estructura extraída
                extracted_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Verificar que el archivo no sea demasiado grande
                        if os.path.getsize(file_path) > 1024 * 1024 * 1024:
                            raise ValueError(f"Archivo extraído demasiado grande: {file}")
                        extracted_files.append(file_path)
                
                # Verificar número total de archivos (límite de 10000)
                if len(extracted_files) > 10000:
                    raise ValueError("Demasiados archivos en el ZIP")
                
                # Verificar tamaño total extraído (límite de 10GB)
                total_size = sum(os.path.getsize(f) for f in extracted_files)
                if total_size > 10 * 1024 * 1024 * 1024:
                    raise ValueError("Contenido total del ZIP demasiado grande")
                
                # Mover archivos del directorio temporal al destino final
                for item in os.listdir(temp_dir):
                    src_path = os.path.join(temp_dir, item)
                    dst_path = os.path.join(download_dir, item)
                    
                    # Evitar sobrescribir archivos existentes
                    if os.path.exists(dst_path):
                        base, ext = os.path.splitext(item)
                        counter = 1
                        while os.path.exists(dst_path):
                            new_name = f"{base}_{counter}{ext}"
                            dst_path = os.path.join(download_dir, new_name)
                            counter += 1
                    
                    shutil.move(src_path, dst_path)
                
                logger.info(f"Extracción completada exitosamente en: {download_dir}")
                return download_dir
                
        except zipfile.BadZipFile:
            logger.error("Archivo ZIP corrupto o inválido")
            return None
        except ValueError as e:
            logger.error(f"Problema de seguridad detectado: {e}")
            return None
        except Exception as e:
            logger.error(f"Error durante la extracción: {e}")
            return None

# Función principal para manejar la subida del usuario
def handle_uploaded_zip(uploaded_file_path: str) -> Optional[str]:
    """
    Maneja un archivo ZIP subido por el usuario.
    
    Args:
        uploaded_file_path: Ruta al archivo ZIP subido
    
    Returns:
        str: Ruta del directorio de extracción si es exitoso
    """
    # Validar que el archivo tenga extensión .zip
    if not uploaded_file_path.lower().endswith('.zip'):
        logger.error("El archivo debe tener extensión .zip")
        return None
    
    # Extraer de forma segura
    return extract_zip_safely(uploaded_file_path)

# Ejemplo de uso:
if __name__ == "__main__":
    # Esta parte sería manejada por el framework web (Flask, Django, etc.)
    # Ejemplo simulado:
    # uploaded_file = request.files['zip_file']
    # temp_path = "/tmp/uploaded.zip"
    # uploaded_file.save(temp_path)
    # result = handle_uploaded_zip(temp_path)
    
    print("Módulo de extracción ZIP seguro cargado.")
    print("Usa handle_uploaded_zip() para procesar archivos subidos.")
