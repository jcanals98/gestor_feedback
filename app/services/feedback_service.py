from sqlalchemy.orm import Session
from app.models.feedback import Feedback
from datetime import datetime
from typing import List


def guardar_feedback(db: Session, autor: str, comentario: str, fecha: datetime, sentimiento: str, etiquetas: list[str], resumen: str):
    
    nuevo_feedback = Feedback(
        autor=autor,
        comentario=comentario,
        fecha=fecha,
        sentimiento=sentimiento,
        etiquetas=",".join(etiquetas), # Convertir lista a texto
        resumen=resumen
    )

    db.add(nuevo_feedback)
    db.commit()
    db.refresh(nuevo_feedback)
    return nuevo_feedback

def obtener_todos_los_feedbacks(db:Session) -> List[Feedback]:
    return db.query(Feedback).order_by(Feedback.fecha.desc()).all()