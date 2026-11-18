import yaml
import os

def read_yaml_file(file_path):
    try:
        with open(file_path, 'r') as file:
            yaml_content = file.read()
            yaml_dict = yaml.safe_load(yaml_content)
            return yaml_dict
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo {file_path} no fue encontrado.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error al procesar el archivo YAML: {e}")
    except Exception as e:
        raise Exception(f"Error inesperado: {e}")

# Ejemplo de uso:
# config = read_yaml_file('config.yaml')
# print(config)
