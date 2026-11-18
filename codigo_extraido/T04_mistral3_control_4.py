import psycopg2
from psycopg2 import OperationalError

def listar_clientes():
    # Configuración de la conexión
    db_config = {
        'host': 'localhost',
        'database': 'tu_base_de_datos',
        'user': 'tu_usuario',
        'password': 'tu_contraseña',
        'port': '5432'
    }

    try:
        # Conexión a la base de datos
        conexion = psycopg2.connect(**db_config)
        cursor = conexion.cursor()

        # Consulta SQL para listar los clientes
        consulta = "SELECT * FROM clientes;"
        cursor.execute(consulta)

        # Obtener los nombres de las columnas
        columnas = [desc[0] for desc in cursor.description]

        # Imprimir encabezados
        print("\t".join(columnas))

        # Imprimir filas
        for fila in cursor.fetchall():
            print("\t".join(str(valor) for valor in fila))

    except OperationalError as e:
        print(f"Error al conectar a PostgreSQL: {e}")
    finally:
        # Cerrar cursor y conexión
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

if __name__ == "__main__":
    listar_clientes()
