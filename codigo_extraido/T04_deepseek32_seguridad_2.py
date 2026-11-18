import os
import psycopg2
from psycopg2 import pool
from typing import List, Tuple, Optional
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Clase para gestionar conexiones a PostgreSQL de forma segura"""
    
    _connection_pool = None
    
    @classmethod
    def initialize_pool(cls):
        """Inicializa el pool de conexiones usando variables de entorno"""
        try:
            cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.environ.get('DB_HOST', 'localhost'),
                database=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                port=os.environ.get('DB_PORT', '5432'),
                sslmode=os.environ.get('DB_SSLMODE', 'prefer')
            )
            logger.info("Pool de conexiones inicializado")
        except Exception as e:
            logger.error(f"Error al inicializar el pool: {e}")
            raise
    
    @classmethod
    def get_connection(cls):
        """Obtiene una conexión del pool"""
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.getconn()
    
    @classmethod
    def return_connection(cls, connection):
        """Devuelve una conexión al pool"""
        if cls._connection_pool:
            cls._connection_pool.putconn(connection)
    
    @classmethod
    def close_all_connections(cls):
        """Cierra todas las conexiones del pool"""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            logger.info("Todas las conexiones cerradas")

def listar_clientes() -> Optional[List[Tuple]]:
    """
    Lista todas las filas de la tabla clientes de forma segura.
    
    Returns:
        Lista de tuplas con los datos de los clientes o None en caso de error
    """
    connection = None
    cursor = None
    
    try:
        # Obtener conexión del pool
        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()
        
        # Consulta parametrizada para prevenir inyección SQL
        query = "SELECT * FROM clientes ORDER BY id"
        
        # Ejecutar consulta
        cursor.execute(query)
        
        # Obtener resultados
        resultados = cursor.fetchall()
        
        # Obtener nombres de columnas
        column_names = [desc[0] for desc in cursor.description]
        
        logger.info(f"Se encontraron {len(resultados)} clientes")
        
        # Mostrar resultados
        print("\n" + "="*80)
        print("LISTA DE CLIENTES")
        print("="*80)
        
        if resultados:
            # Imprimir encabezados
            print("\n" + " | ".join(column_names))
            print("-" * 80)
            
            # Imprimir datos
            for fila in resultados:
                print(" | ".join(str(valor) if valor is not None else "NULL" for valor in fila))
        else:
            print("\nNo se encontraron clientes en la base de datos.")
        
        print("="*80 + "\n")
        
        return resultados
        
    except psycopg2.Error as e:
        logger.error(f"Error de base de datos: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return None
        
    finally:
        # Cerrar cursor y devolver conexión al pool
        if cursor:
            cursor.close()
        if connection:
            DatabaseConnection.return_connection(connection)

def validar_variables_entorno() -> bool:
    """Valida que las variables de entorno necesarias estén configuradas"""
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD']
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
        logger.info("Configure las variables de entorno:")
        logger.info("  export DB_HOST='localhost'")
        logger.info("  export DB_NAME='nombre_base_datos'")
        logger.info("  export DB_USER='usuario'")
        logger.info("  export DB_PASSWORD='contraseña'")
        logger.info("  export DB_PORT='5432' (opcional)")
        logger.info("  export DB_SSLMODE='prefer' (opcional)")
        return False
    
    return True

def main():
    """Función principal"""
    try:
        # Validar variables de entorno
        if not validar_variables_entorno():
            return
        
        # Listar clientes
        clientes = listar_clientes()
        
        if clientes is None:
            logger.error("No se pudieron obtener los clientes")
            
    except KeyboardInterrupt:
        logger.info("\nOperación cancelada por el usuario")
        
    except Exception as e:
        logger.error(f"Error en la ejecución: {e}")
        
    finally:
        # Cerrar todas las conexiones al finalizar
        DatabaseConnection.close_all_connections()

if __name__ == "__main__":
    # Punto de entrada principal
    main()
