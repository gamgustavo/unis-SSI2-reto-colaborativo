import psycopg2
from psycopg2 import sql

def listar_clientes():
    try:
        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(
            dbname="nombre_de_la_base_de_datos",
            user="usuario",
            password="contraseña",
            host="localhost",
            port="5432"
        )

        # Crear un cursor para ejecutar consultas
        cursor = connection.cursor()

        # Escribir la consulta SQL para listar las filas de la tabla clientes
        query = sql.SQL("SELECT * FROM clientes")

        # Ejecutar la consulta
        cursor.execute(query)

        # Obtener todos los resultados
        clientes = cursor.fetchall()

        # Imprimir los resultados
        for cliente in clientes:
            print(cliente)

    except (Exception, psycopg2.Error) as error:
        print("Error al conectar a la base de datos:", error)

    finally:
        # Cerrar el cursor y la conexión
        if connection:
            cursor.close()
            connection.close()

# Llamar a la función para listar los clientes
listar_clientes()
