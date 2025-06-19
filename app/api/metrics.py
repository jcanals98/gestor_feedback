from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import SessionLocal
from app.analytics.estadisticas_service import calcular_resumen_sentimientos


router = APIRouter()

# Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/resumen")
async def metric(db: Session = Depends(get_db)):

    calcular_resumen_sentimientos(db)

    return calcular_resumen_sentimientos(db)