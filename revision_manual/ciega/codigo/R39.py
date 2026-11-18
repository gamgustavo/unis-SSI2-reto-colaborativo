import psycopg2
from psycopg2 import sql, OperationalError
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde un archivo .env
load_dotenv()

class PostgreSQLClient:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self._validate_environment_variables()

    def _validate_environment_variables(self) -> None:
        """Validar que las variables de entorno necesarias estén configuradas."""
        required_vars = [
            'DB_HOST', 'DB_PORT', 'DB_NAME',
            'DB_USER', 'DB_PASSWORD'
        ]
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"La variable de entorno {var} no está configurada")

    def _get_connection_params(self) -> Dict[str, str]:
        """Obtener parámetros de conexión seguros desde variables de entorno."""
        return {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'sslmode': os.getenv('DB_SSL_MODE', 'require'),  # SSL por defecto
            'connect_timeout': 5,
            'application_name': 'client_list_script'
        }

    def connect(self) -> None:
        """Establecer conexión segura a la base de datos."""
        try:
            params = self._get_connection_params()
            self.connection = psycopg2.connect(**params)
            self.connection.autocommit = False  # Desactivar autocommit para transacciones
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("Conexión a la base de datos establecida correctamente")
        except OperationalError as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise

    def disconnect(self) -> None:
        """Cerrar la conexión de manera segura."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Conexión a la base de datos cerrada")

    def get_clients(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Obtener clientes de la tabla clientes de manera segura.

        Args:
            limit: Número máximo de registros a retornar (None para todos)

        Returns:
            Lista de diccionarios con los datos de los clientes
        """
        if not self.connection or self.connection.closed:
            raise OperationalError("No hay conexión activa a la base de datos")

        try:
            # Usar consultas parametrizadas para evitar SQL Injection
            query = sql.SQL("SELECT * FROM clientes")
            params = ()

            if limit is not None:
                query = sql.SQL("SELECT * FROM clientes LIMIT %s")
                params = (limit,)

            self.cursor.execute(query, params)
            clients = self.cursor.fetchall()
            logger.info(f"Se obtuvieron {len(clients)} clientes de la base de datos")
            return clients

        except Exception as e:
            logger.error(f"Error al obtener clientes: {e}")
            self.connection.rollback()
            raise

def main():
    db_client = None
    try:
        db_client = PostgreSQLClient()
        db_client.connect()

        # Obtener clientes con límite seguro (ejemplo: 100 registros)
        clients = db_client.get_clients(limit=100)

        # Mostrar resultados (en producción, manejar esto de forma más segura)
        for client in clients:
            print(client)

    except Exception as e:
        logger.error(f"Error en la ejecución del script: {e}")
    finally:
        if db_client:
            db_client.disconnect()

if __name__ == "__main__":
    main()
