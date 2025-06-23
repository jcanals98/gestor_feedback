from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.models.feedback import Feedback
from app.db.session import SessionLocal
import pandas
from app.utils.utils import model_to_dict_feedback


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calcular_resumen_sentimientos(db: Session):
    # import pdb; pdb.set_trace()

    # Convertimos los registros de feedback a un DataFrame de pandas
    feedbacks_df = pandas.DataFrame(
        model_to_dict_feedback(db.query(Feedback).all())
    )

    # Contamos cuántos hay por cada tipo de sentimiento
    conteo_por_sentimiento = feedbacks_df.value_counts('sentimiento')

    # Calculamos el porcentaje de cada sentimiento respecto al total
    porcentaje_por_sentimiento = (
        (conteo_por_sentimiento / conteo_por_sentimiento.sum()) * 100
    ).round(2).to_dict()

    # Creamos un resumen estructurado por tipo de sentimiento
    resumen_sentimientos = {}
    tipos_sentimiento = ['positivo', 'neutro', 'negativo']
    for tipo in tipos_sentimiento:
        resumen_sentimientos[tipo] = {
            "cantidad": int(conteo_por_sentimiento.get(tipo, 0)),
            "porcentaje": float(porcentaje_por_sentimiento.get(tipo, 0))
        }

    # Construimos el diccionario final con el total de feedbacks y el resumen
    resumen_final = {
        "total_feedbacks": len(feedbacks_df),
        "resumen_por_sentimiento": resumen_sentimientos
    }

    return resumen_final


