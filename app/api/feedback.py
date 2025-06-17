from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.feedback import FeedbackIn, FeedbackOut, FeedbackDB
from app.services.feedback_service import guardar_feedback
from app.db.session import SessionLocal
from app.services.feedback_service import obtener_todos_los_feedbacks

router = APIRouter()

# Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model = FeedbackOut)
async def root(feedback : FeedbackIn, db: Session = Depends(get_db)):
    # Simular análisis IA
    sentimiento = "positivo"
    etiquetas = ["motivación", "equipo"]
    resumen = "El comentario expresa satisfacción con el trabajo en equipo."

    guardar_feedback(
        db=db,
        autor=feedback.autor,
        comentario=feedback.comentario,
        fecha=feedback.fecha,
        sentimiento=sentimiento,
        etiquetas=etiquetas,
        resumen=resumen
    )

    return {
        "sentimiento": sentimiento,
        "etiquetas": etiquetas,
        "resumen": resumen
    }

@router.get("/", response_model=List[FeedbackDB])
async def listar_feedbacks(db: Session = Depends(get_db)):
    return obtener_todos_los_feedbacks(db)