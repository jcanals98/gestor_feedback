from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base_class import Base  # ← Importas el Base global

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    autor = Column(String, nullable=False)
    comentario = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    sentimiento = Column(String, nullable=False)
    etiquetas = Column(String)
    resumen = Column(String)
    respuesta = Column(String, nullable=True)
