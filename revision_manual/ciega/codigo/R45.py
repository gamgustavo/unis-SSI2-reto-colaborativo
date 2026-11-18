import yaml

def leer_archivo_yaml(archivo):
    try:
        with open(archivo, 'r') as file:
            configuracion = yaml.safe_load(file)
            return configuracion
    except FileNotFoundError:
        print("El archivo no fue encontrado.")
        return None
    except yaml.YAMLError as e:
        print(f"Error al parsear el archivo YAML: {e}")
        return None
