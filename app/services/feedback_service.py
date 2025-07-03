from typing import List, Optional
from datetime import datetime, time, date
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

# --- CRUD BÁSICO ---

def guardar_feedback(db: Session, autor: str, comentario: str, fecha: datetime, sentimiento: str, etiquetas: list[str], resumen: str) -> Feedback:
    """
    Guarda un nuevo feedback con análisis IA.
    """
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
    """
    Devuelve todos los feedbacks ordenados por fecha descendente.
    """
    return db.query(Feedback).order_by(Feedback.fecha.desc()).all()


def buscar_feedback_por_id(feedback_id: int, db: Session) -> Feedback:
    """
    Busca un feedback por su ID.
    """
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


def actualizar_feedback_parcial(feedback_id: int, datos_actualizados: dict) -> Feedback:
    """
    Actualiza parcialmente un feedback (solo los campos enviados).
    """
    db = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise ValueError("Feedback no encontrado")

    for campo, valor in datos_actualizados.items():
        if hasattr(feedback, campo) and valor is not None:
            setattr(feedback, campo, valor)

    db.commit()
    db.refresh(feedback)
    return feedback


def eliminar_feedback(feedback_id: int) -> None:
    """
    Elimina un feedback por su ID.
    """
    db = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise ValueError("Feedback no encontrado")

    db.delete(feedback)
    db.commit()


# --- FUNCIONES IA ---

def generar_respuesta_para_feedback(feedback_id: int) -> str:
    """
    Genera y guarda una respuesta empática a un comentario negativo.
    """
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


def generar_sugerencia_para_feedback(feedback_id: int) -> str:
    """
    Genera y guarda una sugerencia concreta para un feedback.
    """
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


def detectar_feedback_toxico(feedback_id: int) -> dict:
    """
    Analiza si un comentario es tóxico y devuelve el resultado.
    """
    db = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise ValueError("Feedback no encontrado")

    return analizar_toxicidad_comentario(feedback.comentario)


def clasificar_urgencia_feedback(feedback_id: int) -> str:
    """
    Clasifica la urgencia de un feedback (urgente, normal, baja) y la guarda.
    """
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
    """
    Analiza los cambios de sentimiento de un autor a lo largo del tiempo.
    """
    feedbacks = db.query(Feedback).filter(Feedback.autor == autor).order_by(Feedback.fecha.asc()).all()

    if not feedbacks:
        raise ValueError("No se encontraron feedbacks para este autor.")

    sentimientos = [f.sentimiento for f in feedbacks]
    conclusion = detectar_cambio_de_sentimiento(sentimientos)

    return {
        "autor": autor,
        "historial": sentimientos,
        "conclusion": conclusion
    }


def filtrar_feedbacks(
    db: Session,
    autor: Optional[str] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    sentimiento: Optional[str] = None,
    urgencia: Optional[str] = None
) -> List[Feedback]:
    """
    Devuelve feedbacks filtrados según parámetros opcionales.
    """
    query = db.query(Feedback)

    if autor:
        query = query.filter(Feedback.autor.ilike(f"%{autor}%"))
    if desde:
        desde_dt = datetime.combine(desde, time.min)
        query = query.filter(Feedback.fecha >= desde_dt)
    if hasta:
        hasta_dt = datetime.combine(hasta, time.max)
        query = query.filter(Feedback.fecha <= hasta_dt)
    if sentimiento:
        query = query.filter(Feedback.sentimiento == sentimiento)
    if urgencia:
        query = query.filter(Feedback.urgencia == urgencia)

    return query.order_by(Feedback.fecha.desc()).all()
