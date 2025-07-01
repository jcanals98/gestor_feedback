from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.user import User
from app.utils.dependencies import get_current_user  
from app.ai.openai_client import analizar_feedback_con_ia
from app.schemas.feedback import FeedbackIn, FeedbackOut, FeedbackDB
from app.services.feedback_service import guardar_feedback
from app.db.session import SessionLocal
from app.services.feedback_service import obtener_todos_los_feedbacks, generar_respuesta_para_feedback, buscar_feedback_por_id

router = APIRouter()

# Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model = FeedbackDB)
async def root(feedback : FeedbackIn, db: Session = Depends(get_db)): #user: User = Depends(get_current_user)

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
def listar_feedbacks(db: Session = Depends(get_db)): #user: User = Depends(get_current_user)
    return obtener_todos_los_feedbacks(db)


@router.get("/{feedback_id}", response_model=FeedbackDB)
def obtener_feedback(feedback_id: int, db: Session = Depends(get_db)): 
    
    feedback = buscar_feedback_por_id(feedback_id, db)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback no encontrado")
    return feedback

    


@router.get("/responder_feedback/{feedback_id}")
def responder_feedback(feedback_id: int):
    try:
        respusta = generar_respuesta_para_feedback(feedback_id)
        print(respusta)
        return {"respuesta": respusta}
    except ValueError as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Error al generar la respuesta")