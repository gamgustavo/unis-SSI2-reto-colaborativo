import psycopg2
from psycopg2.extras import RealDictCursor

def listar_clientes():
    try:
        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(
            dbname="tu_base_de_datos",
            user="tu_usuario",
            password="tu_contraseña",
            host="tu_host",
            port="tu_puerto"
        )

        # Crear un cursor para ejecutar consultas
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Consulta SQL para listar los clientes
            query = "SELECT * FROM clientes"
            
            # Ejecutar la consulta
            cursor.execute(query)
            
            # Obtener todos los resultados
            clientes = cursor.fetchall()
            
            # Imprimir los resultados
            for cliente in clientes:
                print(cliente)
    
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos:", e)
    
    finally:
        # Cerrar la conexión
        if connection:
            connection.close()

# Ejecutar la función
listar_clientes()
