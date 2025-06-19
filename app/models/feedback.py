from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    autor = Column(String, nullable=False)
    comentario = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    sentimiento = Column(String, nullable=False)
    etiquetas = Column(String)
    resumen = Column(String)