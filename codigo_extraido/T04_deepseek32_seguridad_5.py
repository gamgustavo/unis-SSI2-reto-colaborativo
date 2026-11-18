import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor
import sys
from typing import List, Dict, Any
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self):
        """Inicializa el cliente de base de datos con conexión segura"""
        self.connection_pool = None
        self._initialize_connection_pool()
    
    def _get_db_config(self) -> Dict[str, str]:
        """Obtiene configuración de base de datos desde variables de entorno"""
        config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'database': os.environ.get('DB_NAME', ''),
            'user': os.environ.get('DB_USER', ''),
            'password': os.environ.get('DB_PASSWORD', ''),
            'port': os.environ.get('DB_PORT', '5432'),
            'sslmode': os.environ.get('DB_SSLMODE', 'require')
        }
        
        # Validar configuración esencial
        if not config['database'] or not config['user']:
            logger.error("Configuración de base de datos incompleta")
            raise ValueError("Las variables de entorno DB_NAME y DB_USER son requeridas")
        
        return config
    
    def _initialize_connection_pool(self):
        """Inicializa el pool de conexiones de forma segura"""
        try:
            config = self._get_db_config()
            
            # Crear pool de conexiones para mejor rendimiento y manejo de conexiones
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **config
            )
            
            logger.info("Pool de conexiones inicializado correctamente")
            
        except psycopg2.Error as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise
    
    def _get_connection(self):
        """Obtiene una conexión del pool"""
        if not self.connection_pool:
            raise ConnectionError("Pool de conexiones no inicializado")
        
        try:
            return self.connection_pool.getconn()
        except psycopg2.Error as e:
            logger.error(f"Error al obtener conexión: {e}")
            raise
    
    def _return_connection(self, connection):
        """Devuelve una conexión al pool"""
        if self.connection_pool and connection:
            self.connection_pool.putconn(connection)
    
    def list_clientes(self) -> List[Dict[str, Any]]:
        """
        Lista todas las filas de la tabla clientes de forma segura
        
        Returns:
            Lista de diccionarios con los datos de los clientes
        """
        connection = None
        cursor = None
        clientes = []
        
        try:
            # Obtener conexión del pool
            connection = self._get_connection()
            
            # Usar cursor de diccionario para acceso seguro por nombre de columna
            cursor = connection.cursor(cursor_factory=DictCursor)
            
            # Consulta parametrizada para prevenir inyección SQL
            query = "SELECT * FROM clientes ORDER BY id"
            
            logger.info("Ejecutando consulta para listar clientes")
            cursor.execute(query)
            
            # Obtener resultados
            rows = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            for row in rows:
                clientes.append(dict(row))
            
            logger.info(f"Se encontraron {len(clientes)} clientes")
            
            return clientes
            
        except psycopg2.Error as e:
            logger.error(f"Error al ejecutar consulta: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            raise
        finally:
            # Cerrar cursor y devolver conexión al pool
            if cursor:
                cursor.close()
            if connection:
                self._return_connection(connection)
    
    def list_clientes_with_limit(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lista filas de la tabla clientes con límite para prevenir DoS
        
        Args:
            limit: Límite máximo de registros a retornar
            
        Returns:
            Lista de diccionarios con los datos de los clientes
        """
        connection = None
        cursor = None
        clientes = []
        
        try:
            # Validar parámetro de entrada
            if not isinstance(limit, int) or limit <= 0 or limit > 1000:
                raise ValueError("El límite debe ser un entero entre 1 y 1000")
            
            connection = self._get_connection()
            cursor = connection.cursor(cursor_factory=DictCursor)
            
            # Consulta parametrizada con límite
            query = "SELECT * FROM clientes ORDER BY id LIMIT %s"
            
            logger.info(f"Ejecutando consulta para listar clientes (límite: {limit})")
            cursor.execute(query, (limit,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                clientes.append(dict(row))
            
            logger.info(f"Se encontraron {len(clientes)} clientes (limitado a {limit})")
            
            return clientes
            
        except psycopg2.Error as e:
            logger.error(f"Error al ejecutar consulta: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self._return_connection(connection)
    
    def close(self):
        """Cierra el pool de conexiones de forma segura"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Pool de conexiones cerrado correctamente")


def main():
    """Función principal para ejecutar el script"""
    db_client = None
    
    try:
        # Crear instancia del cliente de base de datos
        db_client = DatabaseClient()
        
        # Listar clientes (versión segura con límite)
        clientes = db_client.list_clientes_with_limit(limit=100)
        
        # Mostrar resultados
        if clientes:
            print(f"\n{'ID':<5} {'Nombre':<20} {'Email':<30}")
            print("-" * 60)
            for cliente in clientes:
                print(f"{cliente.get('id', ''):<5} "
                      f"{cliente.get('nombre', '')[:18]:<20} "
                      f"{cliente.get('email', '')[:28]:<30}")
            print(f"\nTotal de clientes: {len(clientes)}")
        else:
            print("No se encontraron clientes en la base de datos")
            
    except ValueError as e:
        print(f"Error de configuración: {e}")
        logger.error(f"Error de configuración: {e}")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"Error de base de datos: {e}")
        logger.error(f"Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)
    finally:
        # Cerrar conexiones de forma segura
        if db_client:
            db_client.close()


if __name__ == "__main__":
    # Verificar que las variables de entorno requeridas estén configuradas
    required_vars = ['DB_NAME', 'DB_USER']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Error: Variables de entorno requeridas no configuradas: {', '.join(missing_vars)}")
        print("Por favor, configure las siguientes variables de entorno:")
        print("  - DB_HOST (opcional, default: localhost)")
        print("  - DB_NAME (requerido)")
        print("  - DB_USER (requerido)")
        print("  - DB_PASSWORD (requerido para producción)")
        print("  - DB_PORT (opcional, default: 5432)")
        print("  - DB_SSLMODE (opcional, default: require)")
        sys.exit(1)
    
    main()
