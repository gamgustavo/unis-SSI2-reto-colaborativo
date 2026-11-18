import yaml
import os

def read_yaml_config(file_path):
    try:
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo {file_path} no existe.")
        
        # Verificar si el archivo es de tipo YAML
        if not file_path.endswith('.yaml') and not file_path.endswith('.yml'):
            raise ValueError(f"El archivo {file_path} no es un archivo YAML válido.")
        
        # Leer el archivo YAML
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        
        return config
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except yaml.YAMLError as e:
        print(f"Error al parsear el archivo YAML: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None
