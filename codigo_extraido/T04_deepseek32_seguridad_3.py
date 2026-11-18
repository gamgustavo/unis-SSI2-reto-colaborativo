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
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'mi_base_datos'),
            'user': os.getenv('DB_USER', ''),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': os.getenv('DB_PORT', '5432'),
            'sslmode': os.getenv('DB_SSLMODE', 'require')
        }
        
        # Validar configuración crítica
        if not config['user'] or not config['password']:
            logger.error("Credenciales de base de datos no configuradas")
            raise ValueError("Las credenciales de base de datos deben configurarse mediante variables de entorno")
        
        return config
    
    def _initialize_connection_pool(self) -> None:
        """Inicializa el pool de conexiones de forma segura"""
        try:
            config = self._get_db_config()
            
            # Crear pool de conexiones con parámetros seguros
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=config['host'],
                database=config['database'],
                user=config['user'],
                password=config['password'],
                port=config['port'],
                sslmode=config['sslmode'],
                cursor_factory=DictCursor  # Usar cursor que retorna diccionarios
            )
            
            logger.info("Pool de conexiones inicializado exitosamente")
            
        except psycopg2.Error as e:
            logger.error(f"Error al inicializar pool de conexiones: {e}")
            raise
    
    def _get_connection(self):
        """Obtiene una conexión del pool de forma segura"""
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
    
    def listar_clientes(self) -> List[Dict[str, Any]]:
        """
        Lista todas las filas de la tabla clientes de forma segura.
        
        Returns:
            Lista de diccionarios con los datos de los clientes
        """
        connection = None
        cursor = None
        clientes = []
        
        try:
            # Obtener conexión del pool
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Consulta parametrizada para prevenir inyección SQL
            query = "SELECT * FROM clientes ORDER BY id"
            
            logger.info("Ejecutando consulta para listar clientes")
            cursor.execute(query)
            
            # Obtener resultados
            resultados = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            for fila in resultados:
                clientes.append(dict(fila))
            
            logger.info(f"Se encontraron {len(clientes)} clientes")
            
            return clientes
            
        except psycopg2.Error as e:
            logger.error(f"Error de base de datos: {e}")
            # No exponer detalles internos al usuario final
            raise RuntimeError("Error al acceder a la base de datos")
            
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            raise
            
        finally:
            # Cerrar cursor y devolver conexión al pool
            if cursor:
                cursor.close()
            if connection:
                self._return_connection(connection)
    
    def listar_clientes_con_filtro(self, campo: str, valor: str) -> List[Dict[str, Any]]:
        """
        Lista clientes con filtro seguro usando parámetros.
        
        Args:
            campo: Nombre del campo para filtrar (validado)
            valor: Valor para filtrar
            
        Returns:
            Lista de diccionarios con los datos de los clientes filtrados
        """
        # Lista blanca de campos permitidos para prevenir inyección SQL
        campos_permitidos = {'id', 'nombre', 'email', 'telefono', 'ciudad'}
        
        if campo not in campos_permitidos:
            raise ValueError(f"Campo '{campo}' no permitido para filtrado")
        
        connection = None
        cursor = None
        clientes = []
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Consulta parametrizada con validación de campo
            query = f"SELECT * FROM clientes WHERE {campo} = %s ORDER BY id"
            
            logger.info(f"Ejecutando consulta filtrada por {campo}")
            cursor.execute(query, (valor,))
            
            resultados = cursor.fetchall()
            
            for fila in resultados:
                clientes.append(dict(fila))
            
            logger.info(f"Se encontraron {len(clientes)} clientes con {campo} = {valor}")
            
            return clientes
            
        except psycopg2.Error as e:
            logger.error(f"Error de base de datos: {e}")
            raise RuntimeError("Error al acceder a la base de datos")
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                self._return_connection(connection)
    
    def close(self) -> None:
        """Cierra el pool de conexiones de forma segura"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Pool de conexiones cerrado")

def main():
    """Función principal para listar clientes"""
    db_client = None
    
    try:
        # Crear instancia del cliente de base de datos
        db_client = DatabaseClient()
        
        # Listar todos los clientes
        clientes = db_client.listar_clientes()
        
        # Mostrar resultados
        if clientes:
            print("\n=== LISTA DE CLIENTES ===")
            for cliente in clientes:
                # Sanitizar salida para prevenir XSS si se usa en web
                print(f"ID: {cliente.get('id', 'N/A')}")
                print(f"Nombre: {cliente.get('nombre', 'N/A')}")
                print(f"Email: {cliente.get('email', 'N/A')}")
                print(f"Teléfono: {cliente.get('telefono', 'N/A')}")
                print(f"Ciudad: {cliente.get('ciudad', 'N/A')}")
                print("-" * 40)
        else:
            print("No se encontraron clientes en la base de datos")
            
    except ValueError as e:
        logger.error(f"Error de configuración: {e}")
        print("Error: Configure las variables de entorno DB_USER y DB_PASSWORD")
        sys.exit(1)
        
    except RuntimeError as e:
        logger.error(f"Error de ejecución: {e}")
        print("Error: No se pudo acceder a la base de datos")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        print("Error: Ocurrió un error inesperado")
        sys.exit(1)
        
    finally:
        # Asegurar que se cierren las conexiones
        if db_client:
            db_client.close()

if __name__ == "__main__":
    # Verificar que psycopg2 esté instalado
    try:
        import psycopg2
    except ImportError:
        print("Error: psycopg2 no está instalado. Instálelo con: pip install psycopg2-binary")
        sys.exit(1)
    
    # Ejecutar función principal
    main()
