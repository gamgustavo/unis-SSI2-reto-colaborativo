import psycopg2

def listar_clientes():
    try:
        # Establecer la conexión a la base de datos
        conexion = psycopg2.connect(
            dbname="nombre_de_la_base_de_datos",
            user="nombre_de_usuario",
            password="contraseña",
            host="localhost",  # o la dirección IP del servidor
            port="5432"        # puerto por defecto de PostgreSQL
        )

        # Crear un cursor para ejecutar comandos SQL
        cursor = conexion.cursor()

        # Ejecutar la consulta SQL para listar los clientes
        cursor.execute("SELECT * FROM clientes")

        # Obtener todos los resultados de la consulta
        clientes = cursor.fetchall()

        # Imprimir los resultados
        for cliente in clientes:
            print(cliente)

    except (Exception, psycopg2.Error) as error:
        print("Error al conectar a la base de datos:", error)

    finally:
        # Cerrar el cursor y la conexión
        if conexion:
            cursor.close()
            conexion.close()

# Llamar a la función para listar los clientes
listar_clientes()
