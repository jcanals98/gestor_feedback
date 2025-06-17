import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import urllib.parse
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Escapar la contraseña para caracteres especiales
if DB_PASSWORD:
    DB_PASSWORD_ESCAPED = urllib.parse.quote_plus(DB_PASSWORD)
else:
    DB_PASSWORD_ESCAPED = ""

# Construir URL con parámetros de codificación
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD_ESCAPED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuración del engine con múltiples codificaciones
def create_engine_with_encoding():
    encodings = ['latin-1', 'windows-1252', 'iso-8859-1', 'utf-8']
    
    for encoding in encodings:
        try:
            engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                connect_args={
                    "options": f"-c client_encoding={encoding}",
                    "client_encoding": encoding,
                    "application_name": "fastapi_feedback_app"
                },
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            # Probar la conexión
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info(f"Conexión exitosa con codificación: {encoding}")
            return engine
            
        except Exception as e:
            logger.warning(f"Fallo con codificación {encoding}: {e}")
            continue
    
    # Si nada funciona, usar configuración por defecto
    logger.error("No se pudo conectar con ninguna codificación")
    return create_engine(SQLALCHEMY_DATABASE_URL)

engine = create_engine_with_encoding()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Función para probar la conexión a la base de datos"""
    try:
        with engine.connect() as connection:
            # Ejecutar una consulta simple para verificar la conexión
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()
            logger.info(f"Conexión exitosa a PostgreSQL: {version[0]}")
            
            # Verificar la codificación
            result = connection.execute(text("SHOW client_encoding"))
            encoding = result.fetchone()
            logger.info(f"Codificación del cliente: {encoding[0]}")
            
            return True
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos: {e}")
        return False