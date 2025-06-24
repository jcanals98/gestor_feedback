from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import SessionLocal
from app.analytics.estadisticas_service import calcular_resumen_sentimientos
from app.models.user import User
from app.utils.dependencies import get_current_user  


router = APIRouter()

# Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/resumen")
async def metric(db: Session = Depends(get_db)): #user: User = Depends(get_current_user)

    calcular_resumen_sentimientos(db)

    return calcular_resumen_sentimientos(db)