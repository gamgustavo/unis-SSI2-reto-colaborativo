import yaml
import io

def leer_configuracion_yaml(archivo_subido):
    """
    Lee un archivo de configuración YAML subido por el usuario y devuelve el diccionario resultante.
    
    Args:
        archivo_subido: Objeto de archivo subido (como el de Flask/Django o similar)
        
    Returns:
        dict: Diccionario con los datos del YAML
        
    Raises:
        yaml.YAMLError: Si hay un error al parsear el YAML
        ValueError: Si el archivo está vacío o no es válido
    """
    try:
        # Verificar que el archivo no esté vacío
        contenido = archivo_subido.read()
        if not contenido:
            raise ValueError("El archivo está vacío")
            
        # Resetear el cursor del archivo para poder leerlo nuevamente
        archivo_subido.seek(0)
        
        # Cargar el contenido YAML
        datos = yaml.safe_load(archivo_subido)
        
        # Si el YAML está vacío o solo contiene comentarios, safe_load devuelve None
        if datos is None:
            return {}
            
        return datos if isinstance(datos, dict) else {"data": datos}
        
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error al parsear YAML: {str(e)}")
    except AttributeError:
        raise ValueError("El objeto proporcionado no es un archivo válido")
    except Exception as e:
        raise ValueError(f"Error al procesar el archivo: {str(e)}")

# Ejemplo de uso (comentado):
# if __name__ == "__main__":
#     # Simular un archivo subido
#     contenido_ejemplo = """
#     database:
#       host: localhost
#       port: 5432
#       name: mydb
#     logging:
#       level: INFO
#       file: app.log
#     """
#     
#     archivo_simulado = io.StringIO(contenido_ejemplo)
#     config = leer_configuracion_yaml(archivo_simulado)
#     print(config)
