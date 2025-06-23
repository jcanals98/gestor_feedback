from app.db.session import engine
from app.models import user, feedback  # Importa modelos para que se registren
from app.db.base_class import Base

def init_db():
    print("🔧 Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente.")

if __name__ == "__main__":
    init_db()
