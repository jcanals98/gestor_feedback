from app.db.session import engine
from app.models.feedback import Base

def init_db():
    Base.metadata.create_all(bind=engine)