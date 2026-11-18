import psycopg2
from psycopg2 import OperationalError

def listar_clientes():
    try:
        # Configuración de la conexión
        conexion = psycopg2.connect(
            host="localhost",
            database="nombre_de_tu_base_de_datos",
            user="tu_usuario",
            password="tu_contraseña"
        )

        # Crear un cursor
        cursor = conexion.cursor()

        # Ejecutar la consulta
        cursor.execute("SELECT * FROM clientes;")

        # Obtener los resultados
        filas = cursor.fetchall()

        # Imprimir los resultados
        for fila in filas:
            print(fila)

    except OperationalError as e:
        print(f"Error al conectar a PostgreSQL: {e}")
    finally:
        # Cerrar el cursor y la conexión
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

if __name__ == "__main__":
    listar_clientes()
