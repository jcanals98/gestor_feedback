import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = urllib.parse.quote_plus(os.getenv("POSTGRES_PASSWORD"))  # Escapa caracteres especiales
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "options": "-c client_encoding=utf8 -c timezone=UTC",
        "client_encoding": "utf8"
    },
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()