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

def extract_zip_safely(zip_file_path: str, extract_to: str = "descargas") -> Optional[str]:
    """
    Extrae de forma segura un archivo ZIP en la carpeta especificada.
    
    Args:
        zip_file_path: Ruta al archivo ZIP
        extract_to: Carpeta donde extraer los contenidos (por defecto 'descargas')
    
    Returns:
        str: Ruta completa a la carpeta de extracción si tiene éxito, None si falla.
    
    Raises:
        ValueError: Si el archivo ZIP no existe o es inválido
        PermissionError: Si no hay permisos para escribir en la carpeta de destino
    """
    
    # Validaciones iniciales
    if not os.path.exists(zip_file_path):
        raise ValueError(f"El archivo {zip_file_path} no existe")
    
    if not zipfile.is_zipfile(zip_file_path):
        raise ValueError(f"El archivo {zip_file_path} no es un ZIP válido")
    
    # Crear carpeta de descargas si no existe
    extract_path = os.path.abspath(extract_to)
    os.makedirs(extract_path, exist_ok=True)
    
    # Verificar permisos de escritura
    if not os.access(extract_path, os.W_OK):
        raise PermissionError(f"No hay permisos de escritura en {extract_path}")
    
    # Usar un directorio temporal intermedio para validación
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # 1. Validar todos los miembros del ZIP antes de extraer
                for member in zip_ref.infolist():
                    # Validar que no sea un path traversal
                    member_path = os.path.normpath(os.path.join(extract_path, member.filename))
                    
                    # Verificar que la ruta extraída esté dentro del directorio destino
                    if not os.path.commonpath([extract_path, member_path]) == extract_path:
                        logger.error(f"Intento de path traversal detectado: {member.filename}")
                        return None
                    
                    # Verificar que no sea un symlink (podría ser un ataque)
                    if member.is_dir():
                        continue
                    
                    # Extraer primero al directorio temporal para inspección
                    zip_ref.extract(member, temp_dir)
                    
                    # Verificar que no sea un archivo ejecutable peligroso (opcional)
                    temp_file_path = os.path.join(temp_dir, member.filename)
                    if os.path.exists(temp_file_path):
                        # Verificar permisos del archivo (no debería ser ejecutable por defecto)
                        if os.access(temp_file_path, os.X_OK):
                            logger.warning(f"Archivo ejecutable detectado: {member.filename}")
                            # Remover permisos de ejecución
                            os.chmod(temp_file_path, 0o644)
                
                # 2. Extraer todo al directorio final
                logger.info(f"Extrayendo {zip_file_path} a {extract_path}")
                zip_ref.extractall(extract_path)
                
                # 3. Limpiar permisos de los archivos extraídos
                for root, dirs, files in os.walk(extract_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Remover permisos de ejecución por defecto
                            os.chmod(file_path, 0o644)
                        except PermissionError:
                            logger.warning(f"No se pudo cambiar permisos de {file_path}")
                    
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            os.chmod(dir_path, 0o755)
                        except PermissionError:
                            logger.warning(f"No se pudo cambiar permisos de {dir_path}")
                
                logger.info(f"Extracción completada exitosamente en {extract_path}")
                return extract_path
                
        except zipfile.BadZipFile:
            logger.error(f"Archivo ZIP corrupto: {zip_file_path}")
            return None
        except PermissionError as e:
            logger.error(f"Error de permisos: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al extraer ZIP: {e}")
            return None

# Ejemplo de uso (comentado):
# if __name__ == "__main__":
#     # Ejemplo de cómo usar la función
#     try:
#         result = extract_zip_safely("archivo.zip", "descargas")
#         if result:
#             print(f"Extraído en: {result}")
#         else:
#             print("Error en la extracción")
#     except Exception as e:
#         print(f"Error: {e}")
