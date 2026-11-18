import psycopg2
from psycopg2 import sql

def listar_clientes():
    try:
        # Configuración de la conexión - modificar según tu entorno
        connection = psycopg2.connect(
            host="localhost",
            database="tu_base_de_datos",
            user="tu_usuario",
            password="tu_contraseña",
            port="5432"
        )
        
        cursor = connection.cursor()
        
        # Consulta para obtener todas las filas de la tabla clientes
        query = sql.SQL("SELECT * FROM clientes")
        cursor.execute(query)
        
        # Obtener todos los resultados
        filas = cursor.fetchall()
        
        # Obtener nombres de columnas
        column_names = [desc[0] for desc in cursor.description]
        
        # Mostrar resultados
        print("Filas de la tabla 'clientes':")
        print("-" * 50)
        
        # Imprimir nombres de columnas
        print(" | ".join(column_names))
        print("-" * 50)
        
        # Imprimir cada fila
        for fila in filas:
            print(" | ".join(str(valor) for valor in fila))
        
        print(f"\nTotal de filas: {len(filas)}")
        
    except psycopg2.Error as e:
        print(f"Error al conectar a PostgreSQL: {e}")
    finally:
        # Cerrar cursor y conexión
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    listar_clientes()
