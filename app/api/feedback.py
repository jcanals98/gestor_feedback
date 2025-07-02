from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.user import User
from app.utils.dependencies import get_current_user
from app.schemas.feedback import FeedbackIn, FeedbackOut, FeedbackDB
from app.services.feedback_service import (
    guardar_feedback,
    obtener_todos_los_feedbacks,
    buscar_feedback_por_id,
    generar_respuesta_para_feedback,
    generar_sugerencia_para_feedback,
    detectar_feedback_toxico,
    clasificar_urgencia_feedback,
    detectar_cambios_sentimiento
)
from app.ai.openai_client import analizar_feedback_con_ia
from app.db.session import SessionLocal

router = APIRouter()


# Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Crear un nuevo feedback con análisis automático de IA
@router.post("/", response_model=FeedbackDB)
async def crear_feedback(feedback: FeedbackIn, db: Session = Depends(get_db)):
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


# Listar todos los feedbacks ordenados por fecha descendente
@router.get("/", response_model=List[FeedbackDB])
def listar_feedbacks(db: Session = Depends(get_db)):
    return obtener_todos_los_feedbacks(db)


# Obtener un único feedback por su ID
@router.get("/{feedback_id}", response_model=FeedbackDB)
def obtener_feedback(feedback_id: int, db: Session = Depends(get_db)):
    feedback = buscar_feedback_por_id(feedback_id, db)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback no encontrado")
    return feedback


# Generar respuesta educada para feedback negativo
@router.post("/responder_feedback/{feedback_id}")
def responder_feedback(feedback_id: int):
    try:
        respuesta = generar_respuesta_para_feedback(feedback_id)
        return {"respuesta": respuesta}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Error al generar la respuesta")


# Sugerencia constructiva generada por IA
@router.post("/sugerencia_feedback/{feedback_id}")
def sugerencia_feedback(feedback_id: int):
    try:
        sugerencia = generar_sugerencia_para_feedback(feedback_id)
        return {"sugerencia": sugerencia}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Error al generar la sugerencia")


# Detectar si un comentario contiene lenguaje tóxico
@router.post("/detectar_toxico/{feedback_id}")
def detectar_toxico(feedback_id: int):
    try:
        resultado = detectar_feedback_toxico(feedback_id)
        return resultado
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Error al analizar toxicidad del comentario")


# Clasificar el nivel de urgencia de un feedback
@router.post("/clasificar_urgencia/{feedback_id}")
def clasificar_urgencia(feedback_id: int):
    try:
        urgencia = clasificar_urgencia_feedback(feedback_id)
        return {"urgencia": urgencia}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR INTERNO:", str(e))
        raise HTTPException(status_code=500, detail="Error al clasificar urgencia")


# Detectar cambios de actitud de un autor a lo largo del tiempo
@router.post("/detectar_sentimientos_cambiantes/{autor}")
def detectar_sentimiento_cambiante(autor: str, db: Session = Depends(get_db)):
    try:
        resultado = detectar_cambios_sentimiento(autor, db)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al analizar sentimientos")
