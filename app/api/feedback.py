from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.models.user import User
from app.utils.dependencies import get_current_user
from app.schemas.feedback import FeedbackIn, FeedbackOut, FeedbackDB, FeedbackUpdate
from app.services.feedback_service import (
    guardar_feedback,
    obtener_todos_los_feedbacks,
    buscar_feedback_por_id,
    generar_respuesta_para_feedback,
    generar_sugerencia_para_feedback,
    detectar_feedback_toxico,
    clasificar_urgencia_feedback,
    detectar_cambios_sentimiento,
    actualizar_feedback_parcial,
    eliminar_feedback,
    filtrar_feedbacks
)
from app.ai.openai_client import analizar_feedback_con_ia
from app.db.session import SessionLocal

router = APIRouter()


# --- Dependencia para sesión de base de datos ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- CRUD BÁSICO ---

@router.post("/", response_model=FeedbackDB)
async def crear_feedback(feedback: FeedbackIn, db: Session = Depends(get_db)):
    """
    Crea un nuevo feedback y ejecuta análisis IA (sentimiento, etiquetas, resumen).
    """
    analisis = await analizar_feedback_con_ia(feedback.comentario)
    fecha_final = feedback.fecha or datetime.now()

    nuevo_feedback = guardar_feedback(
        db=db,
        autor=feedback.autor,
        comentario=feedback.comentario,
        fecha=fecha_final,
        sentimiento=analisis["sentimiento"],
        etiquetas=analisis["etiquetas"],
        resumen=analisis["resumen"],
    )
    return nuevo_feedback


@router.get("/", response_model=List[FeedbackDB])
def listar_feedbacks(db: Session = Depends(get_db)):
    """
    Lista todos los feedbacks ordenados por fecha descendente.
    """
    return obtener_todos_los_feedbacks(db)


@router.get("/{feedback_id}", response_model=FeedbackDB)
def obtener_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un feedback por su ID.
    """
    feedback = buscar_feedback_por_id(feedback_id, db)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback no encontrado")
    return feedback


@router.patch("/{feedback_id}", response_model=FeedbackDB)
def feedback_actualizado(feedback_id: int, datos: FeedbackUpdate):
    """
    Actualiza parcialmente un feedback existente (PATCH).
    """
    try:
        feedback_actualizado = actualizar_feedback_parcial(feedback_id, datos.dict(exclude_unset=True))
        return feedback_actualizado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR AL ACTUALIZAR:", str(e))
        raise HTTPException(status_code=500, detail="Error al actualizar el feedback")


@router.delete("/{feedback_id}")
def eliminar_feedback_endpoint(feedback_id: int):
    """
    Elimina un feedback existente por su ID.
    """
    try:
        eliminar_feedback(feedback_id)
        return {"detail": f"Feedback {feedback_id} eliminado correctamente"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR AL ELIMINAR:", str(e))
        raise HTTPException(status_code=500, detail="Error al eliminar el feedback")


# --- FILTRADO AVANZADO ---

@router.get("/filtrados", response_model=List[FeedbackDB])
def filtrar_feedbacks_endpoint(
    autor: Optional[str] = Query(default=None, description="Filtrar por autor"),
    desde: Optional[date] = Query(default=None, description="Fecha mínima YYYY-MM-DD"),
    hasta: Optional[date] = Query(default=None, description="Fecha máxima YYYY-MM-DD"),
    sentimiento: Optional[str] = Query(default=None, description="positivo, negativo o neutro"),
    urgencia: Optional[str] = Query(default=None, description="urgente, normal o baja"),
    db: Session = Depends(get_db)
):
    """
    Devuelve feedbacks filtrados por autor, rango de fechas, sentimiento y/o urgencia.
    """
    try:
        feedbacks = filtrar_feedbacks(db, autor, desde, hasta, sentimiento, urgencia)
        return feedbacks
    except Exception as e:
        print("ERROR AL FILTRAR:", str(e))
        raise HTTPException(status_code=500, detail="Error al filtrar feedbacks")


# --- FUNCIONES IA ---

@router.post("/responder_feedback/{feedback_id}")
def responder_feedback(feedback_id: int):
    """
    Genera una respuesta empática para un comentario negativo.
    """
    try:
        respuesta = generar_respuesta_para_feedback(feedback_id)
        return {"respuesta": respuesta}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Error al generar la respuesta")


@router.post("/sugerencia_feedback/{feedback_id}")
def sugerencia_feedback(feedback_id: int):
    """
    Genera una sugerencia de mejora basada en el comentario.
    """
    try:
        sugerencia = generar_sugerencia_para_feedback(feedback_id)
        return {"sugerencia": sugerencia}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Error al generar la sugerencia")


@router.post("/detectar_toxico/{feedback_id}")
def detectar_toxico(feedback_id: int):
    """
    Detecta si el comentario contiene lenguaje tóxico.
    """
    try:
        resultado = detectar_feedback_toxico(feedback_id)
        return resultado
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Error al analizar toxicidad del comentario")


@router.post("/clasificar_urgencia/{feedback_id}")
def clasificar_urgencia(feedback_id: int):
    """
    Clasifica el nivel de urgencia de un feedback (urgente, normal, baja).
    """
    try:
        urgencia = clasificar_urgencia_feedback(feedback_id)
        return {"urgencia": urgencia}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR INTERNO:", str(e))
        raise HTTPException(status_code=500, detail="Error al clasificar urgencia")


@router.post("/detectar_sentimientos_cambiantes/{autor}")
def detectar_sentimiento_cambiante(autor: str, db: Session = Depends(get_db)):
    """
    Analiza la evolución del sentimiento de un autor a lo largo del tiempo.
    """
    try:
        resultado = detectar_cambios_sentimiento(autor, db)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al analizar sentimientos")
