import os
import tempfile
import uuid
import logging
from typing import Optional, Union, Dict, List, Any
import json
import csv
import pickle

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_report_data(
    data: Union[Dict[str, Any], List[Any], str, bytes],
    file_format: str = 'json',
    filename_prefix: str = 'report_',
    filename_suffix: Optional[str] = None,
    directory: Optional[str] = None,
    encoding: str = 'utf-8'
) -> str:
    """
    Guarda datos de un reporte en un archivo temporal de forma segura.
    
    Args:
        data: Datos a guardar. Puede ser dict, list, str o bytes.
        file_format: Formato del archivo ('json', 'csv', 'txt', 'binary').
        filename_prefix: Prefijo para el nombre del archivo.
        filename_suffix: Sufijo para el nombre del archivo (incluyendo extensión).
        directory: Directorio donde crear el archivo temporal. Si es None, usa el directorio temporal del sistema.
        encoding: Codificación para archivos de texto.
    
    Returns:
        str: Ruta completa al archivo temporal creado.
    
    Raises:
        ValueError: Si el formato no es soportado o los datos no son válidos.
        OSError: Si hay problemas al crear o escribir el archivo.
        TypeError: Si los datos no son compatibles con el formato especificado.
    """
    
    # Validaciones de seguridad
    if not filename_prefix or not isinstance(filename_prefix, str):
        raise ValueError("El prefijo del nombre de archivo debe ser una cadena no vacía")
    
    if filename_suffix and not isinstance(filename_suffix, str):
        raise ValueError("El sufijo del nombre de archivo debe ser una cadena")
    
    # Limpiar el prefijo para evitar problemas de seguridad
    filename_prefix = ''.join(c for c in filename_prefix if c.isalnum() or c in '._-')
    if not filename_prefix:
        filename_prefix = 'report_'
    
    # Validar formato
    supported_formats = ['json', 'csv', 'txt', 'binary']
    if file_format not in supported_formats:
        raise ValueError(f"Formato no soportado. Usa uno de: {supported_formats}")
    
    # Crear directorio temporal seguro si no se especifica
    if directory:
        if not os.path.isdir(directory):
            raise ValueError(f"El directorio especificado no existe: {directory}")
        if not os.access(directory, os.W_OK):
            raise ValueError(f"No se tiene permiso de escritura en el directorio: {directory}")
    
    try:
        # Crear archivo temporal con nombre seguro
        if filename_suffix:
            # Validar que el sufijo no contenga caracteres peligrosos
            safe_suffix = ''.join(c for c in filename_suffix if c.isalnum() or c in '._-')
            if safe_suffix != filename_suffix:
                logger.warning("Caracteres no seguros eliminados del sufijo del nombre de archivo")
        else:
            safe_suffix = f".{file_format}"
        
        # Usar NamedTemporaryFile con delete=False para control manual
        with tempfile.NamedTemporaryFile(
            mode='wb' if file_format == 'binary' else 'w',
            prefix=filename_prefix,
            suffix=safe_suffix,
            dir=directory,
            delete=False,
            encoding=None if file_format == 'binary' else encoding
        ) as temp_file:
            file_path = temp_file.name
            
            # Escribir datos según el formato
            if file_format == 'json':
                if isinstance(data, (dict, list)):
                    json.dump(data, temp_file, ensure_ascii=False, indent=2)
                elif isinstance(data, str):
                    # Validar que sea JSON válido
                    json.loads(data)  # Validación
                    temp_file.write(data)
                else:
                    raise TypeError("Para formato JSON, los datos deben ser dict, list o str JSON válido")
            
            elif file_format == 'csv':
                if isinstance(data, list):
                    if not data:
                        # Lista vacía
                        writer = csv.writer(temp_file)
                    elif isinstance(data[0], dict):
                        # Lista de diccionarios
                        fieldnames = list(data[0].keys())
                        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(data)
                    elif isinstance(data[0], list):
                        # Lista de listas
                        writer = csv.writer(temp_file)
                        writer.writerows(data)
                    else:
                        raise TypeError("Para formato CSV, los datos deben ser lista de listas o lista de diccionarios")
                else:
                    raise TypeError("Para formato CSV, los datos deben ser una lista")
            
            elif file_format == 'txt':
                if isinstance(data, str):
                    temp_file.write(data)
                elif isinstance(data, bytes):
                    # Decodificar bytes a string si es posible
                    try:
                        text_data = data.decode(encoding)
                        temp_file.write(text_data)
                    except UnicodeDecodeError:
                        raise TypeError("Los datos bytes no pueden ser decodificados con la codificación especificada")
                else:
                    # Convertir otros tipos a string
                    temp_file.write(str(data))
            
            elif file_format == 'binary':
                if isinstance(data, bytes):
                    temp_file.write(data)
                elif isinstance(data, str):
                    temp_file.write(data.encode(encoding))
                else:
                    # Usar pickle solo si es necesario y con precaución
                    logger.warning("Usando pickle para serialización binaria. Solo use con datos confiables.")
                    pickle.dump(data, temp_file, protocol=pickle.HIGHEST_PROTOCOL)
            
            logger.info(f"Archivo temporal creado: {file_path}")
            return file_path
    
    except (IOError, OSError) as e:
        logger.error(f"Error al crear o escribir el archivo temporal: {e}")
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.error(f"Error en los datos o formato: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise


def cleanup_temp_file(file_path: str) -> None:
    """
    Elimina de forma segura un archivo temporal creado por save_report_data.
    
    Args:
        file_path: Ruta al archivo temporal a eliminar.
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Archivo temporal eliminado: {file_path}")
    except OSError as e:
        logger.error(f"Error al eliminar el archivo temporal {file_path}: {e}")


# Ejemplo de uso seguro
if __name__ == "__main__":
    try:
        # Ejemplo 1: Guardar datos JSON
        report_data = {
            "id": str(uuid.uuid4()),
            "title": "Reporte de seguridad",
            "items": ["item1", "item2", "item3"],
            "metadata": {
                "created_at": "2024-01-01",
                "version": "1.0"
            }
        }
        
        json_file = save_report_data(report_data, file_format='json')
        print(f"Archivo JSON creado: {json_file}")
        
        # Ejemplo 2: Guardar datos CSV
        csv_data = [
            ["Nombre", "Edad", "Ciudad"],
            ["Alice", "30", "Madrid"],
            ["Bob", "25", "Barcelona"]
        ]
        
        csv_file = save_report_data(csv_data, file_format='csv')
        print(f"Archivo CSV creado: {csv_file}")
        
        # Limpiar archivos temporales después de usarlos
        cleanup_temp_file(json_file)
        cleanup_temp_file(csv_file)
        
    except Exception as e:
        print(f"Error: {e}")
