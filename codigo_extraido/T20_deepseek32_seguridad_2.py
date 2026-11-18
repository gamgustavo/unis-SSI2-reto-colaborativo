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

def extract_zip_safely(zip_path: str, extract_to: str = 'descargas') -> Optional[str]:
    """
    Extrae de forma segura un archivo ZIP en la carpeta especificada.
    
    Args:
        zip_path: Ruta al archivo ZIP
        extract_to: Carpeta donde extraer el contenido (por defecto 'descargas')
    
    Returns:
        str: Ruta completa a la carpeta de extracción si tiene éxito, None si falla.
    
    Raises:
        ValueError: Si el archivo no es ZIP o está corrupto
        PermissionError: Si no hay permisos de escritura
        OSError: Para otros errores del sistema
    """
    
    # Validaciones iniciales
    if not os.path.exists(zip_path):
        logger.error(f"El archivo no existe: {zip_path}")
        return None
    
    if not zipfile.is_zipfile(zip_path):
        logger.error(f"El archivo no es un ZIP válido: {zip_path}")
        raise ValueError("El archivo no es un ZIP válido")
    
    # Crear directorio de descargas si no existe
    extract_path = os.path.abspath(extract_to)
    os.makedirs(extract_path, exist_ok=True)
    
    # Verificar permisos de escritura
    if not os.access(extract_path, os.W_OK):
        logger.error(f"No hay permisos de escritura en: {extract_path}")
        raise PermissionError(f"No hay permisos de escritura en {extract_path}")
    
    # Usar directorio temporal para extracción intermedia
    temp_dir = None
    try:
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp(prefix="zip_extract_")
        logger.info(f"Directorio temporal creado: {temp_dir}")
        
        # Abrir archivo ZIP con validaciones
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Verificar que el ZIP no esté vacío
            if len(zip_ref.namelist()) == 0:
                logger.error("El archivo ZIP está vacío")
                raise ValueError("El archivo ZIP está vacío")
            
            # Validar cada archivo en el ZIP antes de extraer
            for file_info in zip_ref.infolist():
                # Prevenir path traversal attacks
                safe_filename = os.path.normpath(file_info.filename)
                if safe_filename.startswith(('..', '/', '\\')) or '..' in safe_filename:
                    logger.error(f"Intento de path traversal detectado: {file_info.filename}")
                    raise ValueError(f"Nombre de archivo no seguro: {file_info.filename}")
                
                # Construir ruta completa de destino
                full_path = os.path.join(temp_dir, safe_filename)
                
                # Prevenir extracción fuera del directorio temporal
                if not os.path.commonpath([temp_dir, os.path.abspath(full_path)]) == temp_dir:
                    logger.error(f"Intento de extraer fuera del directorio: {file_info.filename}")
                    raise ValueError(f"Ruta de extracción no segura: {file_info.filename}")
                
                # Verificar que no sea un enlace simbólico malicioso
                if file_info.is_symlink():
                    logger.error(f"Enlace simbólico detectado y rechazado: {file_info.filename}")
                    raise ValueError("Los enlaces simbólicos no están permitidos")
            
            # Extraer todos los archivos al directorio temporal
            zip_ref.extractall(temp_dir)
            logger.info(f"Archivos extraídos a directorio temporal: {len(zip_ref.namelist())} archivos")
        
        # Mover archivos del directorio temporal al destino final
        for item in os.listdir(temp_dir):
            src_path = os.path.join(temp_dir, item)
            dst_path = os.path.join(extract_path, item)
            
            # Si ya existe, añadir sufijo numérico
            counter = 1
            original_dst = dst_path
            while os.path.exists(dst_path):
                name, ext = os.path.splitext(item)
                dst_path = os.path.join(extract_path, f"{name}_{counter}{ext}")
                counter += 1
            
            if src_path != dst_path:
                shutil.move(src_path, dst_path)
                logger.info(f"Movido: {item} -> {os.path.basename(dst_path)}")
        
        logger.info(f"Extracción completada exitosamente en: {extract_path}")
        return extract_path
        
    except zipfile.BadZipFile as e:
        logger.error(f"Archivo ZIP corrupto: {e}")
        raise ValueError("El archivo ZIP está corrupto o no es válido")
    
    except Exception as e:
        logger.error(f"Error durante la extracción: {e}")
        raise
    
    finally:
        # Limpiar directorio temporal si existe
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Directorio temporal eliminado: {temp_dir}")
            except Exception as e:
                logger.warning(f"No se pudo eliminar el directorio temporal: {e}")

# Ejemplo de uso (comentado para evitar ejecución accidental)
"""
if __name__ == "__main__":
    try:
        # En un caso real, el archivo vendría de una carga del usuario
        # Por ejemplo: uploaded_file = request.files['file']
        
        # Simulación: extraer un archivo llamado 'archivo.zip'
        result = extract_zip_safely('archivo.zip', 'descargas')
        if result:
            print(f"Extracción exitosa en: {result}")
    except Exception as e:
        print(f"Error: {e}")
"""
