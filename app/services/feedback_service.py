from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.ai.openai_client import generar_respuesta_educada
from app.db.session import SessionLocal



def guardar_feedback(db: Session, autor: str, comentario: str, fecha: datetime, sentimiento: str, etiquetas: list[str], resumen: str):
    nuevo_feedback = Feedback(
        autor=autor,
        comentario=comentario,
        fecha=fecha,
        sentimiento=sentimiento,
        etiquetas=",".join(etiquetas),
        resumen=resumen
    )
    db.add(nuevo_feedback)
    db.commit()
    db.refresh(nuevo_feedback)
    return nuevo_feedback


def obtener_todos_los_feedbacks(db: Session) -> List[Feedback]:
    return db.query(Feedback).order_by(Feedback.fecha.desc()).all()


def buscar_feedback_por_id(feedback_id:int, db: Session) -> Feedback:
    
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    return feedback


def generar_respuesta_para_feedback(feedback_id: int) -> str:
    db = SessionLocal()

    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:  
        raise ValueError("Feedback no encontrado")
    
    if feedback.sentimiento != "negativo":
        raise ValueError("Solo se generan respuestas para comentarios negativos")
    
    respuesta = generar_respuesta_educada(feedback.comentario)

    feedback.respuesta = respuesta
    db.commit()
    db.refresh(feedback)

    return respuesta
