import os
import psycopg2
from psycopg2 import pool
from typing import List, Tuple, Optional
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseClient:
    """Cliente seguro para conexión a base de datos PostgreSQL"""
    
    def __init__(self):
        """Inicializa el cliente con configuración desde variables de entorno"""
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializa el pool de conexiones de forma segura"""
        try:
            # Obtener credenciales desde variables de entorno (no hardcodeadas)
            db_host = os.environ.get('DB_HOST', 'localhost')
            db_port = os.environ.get('DB_PORT', '5432')
            db_name = os.environ.get('DB_NAME', 'mi_base_datos')
            db_user = os.environ.get('DB_USER')
            db_password = os.environ.get('DB_PASSWORD')
            
            # Validar que tenemos las credenciales mínimas
            if not db_user or not db_password:
                raise ValueError("Credenciales de base de datos no configuradas en variables de entorno")
            
            # Crear pool de conexiones con parámetros seguros
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
                # Parámetros de seguridad adicionales
                sslmode=os.environ.get('DB_SSLMODE', 'prefer'),
                connect_timeout=10
            )
            
            logger.info("Pool de conexiones inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar el pool de conexiones: {e}")
            raise
    
    def get_clientes(self) -> List[Tuple]:
        """
        Obtiene todas las filas de la tabla clientes de forma segura
        
        Returns:
            Lista de tuplas con los datos de los clientes
        """
        connection = None
        cursor = None
        clientes = []
        
        try:
            # Obtener conexión del pool
            connection = self.connection_pool.getconn()
            cursor = connection.cursor()
            
            # Consulta parametrizada para prevenir inyección SQL
            query = "SELECT * FROM clientes ORDER BY id"
            
            # Ejecutar consulta
            cursor.execute(query)
            
            # Obtener resultados
            clientes = cursor.fetchall()
            
            # Registrar actividad (sin datos sensibles)
            logger.info(f"Se obtuvieron {len(clientes)} clientes")
            
            # Obtener nombres de columnas para referencia
            column_names = [desc[0] for desc in cursor.description]
            logger.debug(f"Columnas: {column_names}")
            
        except psycopg2.Error as e:
            logger.error(f"Error de base de datos: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            raise
        finally:
            # Siempre cerrar cursor y devolver conexión al pool
            if cursor:
                cursor.close()
            if connection:
                self.connection_pool.putconn(connection)
        
        return clientes
    
    def get_clientes_limitados(self, limite: int = 100) -> List[Tuple]:
        """
        Obtiene filas de la tabla clientes con límite para prevenir DoS
        
        Args:
            limite: Número máximo de filas a retornar
            
        Returns:
            Lista de tuplas con los datos de los clientes
        """
        connection = None
        cursor = None
        clientes = []
        
        try:
            # Validar parámetro de entrada
            if not isinstance(limite, int) or limite <= 0 or limite > 1000:
                raise ValueError("El límite debe ser un entero entre 1 y 1000")
            
            connection = self.connection_pool.getconn()
            cursor = connection.cursor()
            
            # Consulta parametrizada con límite
            query = "SELECT * FROM clientes ORDER BY id LIMIT %s"
            
            # Ejecutar con parámetro para prevenir inyección SQL
            cursor.execute(query, (limite,))
            
            clientes = cursor.fetchall()
            logger.info(f"Se obtuvieron {len(clientes)} clientes (límite: {limite})")
            
        except (psycopg2.Error, ValueError) as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.connection_pool.putconn(connection)
        
        return clientes
    
    def close_all_connections(self):
        """Cierra todas las conexiones del pool de forma segura"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Todas las conexiones del pool han sido cerradas")

def main():
    """Función principal con manejo seguro de errores"""
    db_client = None
    
    try:
        # Crear instancia del cliente
        db_client = DatabaseClient()
        
        # Obtener clientes (versión segura con límite)
        clientes = db_client.get_clientes_limitados(limite=100)
        
        # Mostrar resultados (sin información sensible)
        print(f"\nTotal de clientes obtenidos: {len(clientes)}")
        print("-" * 50)
        
        if clientes:
            # Mostrar solo las primeras 5 filas como ejemplo
            for i, cliente in enumerate(clientes[:5], 1):
                # Enmascarar datos sensibles si es necesario
                cliente_enmascarado = list(cliente)
                # Ejemplo: enmascarar email si está en la posición 2
                if len(cliente_enmascarado) > 2 and '@' in str(cliente_enmascarado[2]):
                    email = str(cliente_enmascarado[2])
                    usuario, dominio = email.split('@')
                    cliente_enmascarado[2] = f"{usuario[:2]}***@{dominio}"
                
                print(f"Cliente {i}: {cliente_enmascarado}")
            
            if len(clientes) > 5:
                print(f"... y {len(clientes) - 5} clientes más")
        
        print("-" * 50)
        
    except ValueError as e:
        logger.error(f"Error de configuración: {e}")
        print("Error: Verifique las variables de entorno DB_USER y DB_PASSWORD")
    except psycopg2.OperationalError as e:
        logger.error(f"Error de conexión: {e}")
        print("Error: No se pudo conectar a la base de datos")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        print(f"Error: {e}")
    finally:
        # Asegurar que se cierren las conexiones
        if db_client:
            db_client.close_all_connections()

if __name__ == "__main__":
    # Verificar variables de entorno críticas antes de ejecutar
    required_vars = ['DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Error: Variables de entorno requeridas no configuradas: {', '.join(missing_vars)}")
        print("Por favor, configure:")
        for var in missing_vars:
            print(f"  export {var}=tu_valor")
    else:
        main()
