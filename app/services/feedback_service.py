from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.ai.openai_client import (
    generar_respuesta_educada,
    generar_sugerencia_para_comentario,
    analizar_toxicidad_comentario,
    clasificar_nivel_urgencia,
    detectar_cambio_de_sentimiento
)
from app.db.session import SessionLocal

# Guarda un nuevo registro de feedback con análisis IA ya procesado
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

# Devuelve todos los registros de feedback ordenados por fecha descendente
def obtener_todos_los_feedbacks(db: Session) -> List[Feedback]:
    return db.query(Feedback).order_by(Feedback.fecha.desc()).all()

# Busca un feedback por ID
def buscar_feedback_por_id(feedback_id: int, db: Session) -> Feedback:
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()

# Genera una respuesta educada a un comentario negativo (y la guarda)
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

# Genera una sugerencia concreta para el feedback (y la guarda)
def generar_sugerencia_para_feedback(feedback_id: int) -> str:
    db = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise ValueError("Feedback no encontrado")

    if feedback.sugerencia:
        return feedback.sugerencia

    sugerencia = generar_sugerencia_para_comentario(feedback.comentario)
    feedback.sugerencia = sugerencia
    db.commit()
    db.refresh(feedback)

    return sugerencia

# Analiza si el comentario es tóxico y por qué
def detectar_feedback_toxico(feedback_id: int) -> dict:
    db = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise ValueError("Feedback no encontrado")

    return analizar_toxicidad_comentario(feedback.comentario)

def clasificar_urgencia_feedback(feedback_id: int) -> str:
    db = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise ValueError("Feedback no encontrado")
    
    urgencia = clasificar_nivel_urgencia(feedback.comentario)
    feedback.urgencia = urgencia
    db.commit()
    db.refresh(feedback)

    return urgencia

def detectar_cambios_sentimiento(autor: str, db: Session) -> dict:
    feedbacks = db.query(Feedback).filter(Feedback.autor == autor).order_by(Feedback.fecha.asc()).all()

    if not feedbacks:
        raise ValueError("No se encontraron feedbacks para este autor.")
    
    """
        historial = [f.sentimiento for f in feedbacks]

        cambios_detectados = any(historial[i] != historial[i + 1] for i in range(len(historial) - 1))

        conclusion = ""
        if not cambios_detectados:
            conclusion = "No se detectan cambios de sentimiento."
        elif historial[-1] == "negativo":
            conclusion = "El sentimiento ha empeorado con el tiempo."
        elif historial[0] == "negativo" and historial[-1] == "positivo":
            conclusion = "El sentimiento ha mejorado con el tiempo."
        else:
            conclusion = "Se detectan variaciones en el sentimiento del autor."
    """


    sentimientos = [f.sentimiento for f in feedbacks]

    conclusion = detectar_cambio_de_sentimiento(sentimientos)

    return {
        "autor": autor,
        "historial": sentimientos,
        "conclusion": conclusion
    }

