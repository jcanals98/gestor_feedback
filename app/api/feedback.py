from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.ai.openai_client import analizar_feedback_con_ia
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

@router.post("/", response_model = FeedbackDB)
async def root(feedback : FeedbackIn, db: Session = Depends(get_db)):

    analisis  = await analizar_feedback_con_ia(feedback.comentario)

    # Si no se envió fecha, usar la actual
    fecha_final = feedback.fecha or datetime.now()

    nuevo_feedback = guardar_feedback(
        db=db,
        autor=feedback.autor,
        comentario=feedback.comentario,
        fecha=fecha_final,
        sentimiento=analisis["sentimiento"],
        etiquetas=analisis["etiquetas"],
        resumen=analisis["resumen"]
    )

    return nuevo_feedback

@router.get("/", response_model=List[FeedbackDB])
async def listar_feedbacks(db: Session = Depends(get_db)):
    return obtener_todos_los_feedbacks(db)