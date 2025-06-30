from typing import List
from datetime import datetime
import re
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.utils.dependencies import get_db
import pandas as pd

from app.db.session import SessionLocal
from app.models.feedback import Feedback
from app.analytics.estadisticas_service import calcular_resumen_sentimientos

router = APIRouter()

# Dependencia reutilizable para obtener la sesión de base de datos


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/resumen", summary="Resumen general de sentimientos (IA)")
async def obtener_resumen_sentimientos(db: Session = Depends(get_db)):
    """
    Devuelve un resumen generado por IA con el análisis de sentimientos.
    Se delega la lógica a `calcular_resumen_sentimientos`, donde se procesan todos los comentarios.
    """
    resumen = calcular_resumen_sentimientos(db)
    return resumen


@router.get("/general", summary="Cantidad de feedbacks por sentimiento")
async def metricas_generales(db: Session = Depends(get_db)):
    """
    Cuenta cuántos comentarios hay por tipo de sentimiento (positivo, negativo, neutral).
    Devuelve también el total acumulado.
    """
    resultados = (
        db.query(Feedback.sentimiento, func.count(Feedback.id))
        .group_by(Feedback.sentimiento)
        .all()
    )

    # Convertimos la lista de tuplas a un diccionario
    resumen = {sentimiento: cantidad for sentimiento, cantidad in resultados}
    resumen["total"] = sum(resumen.values())

    return resumen


@router.get("/por_usuario", summary="Resumen de sentimientos por usuario")
async def metricas_por_usuario(nombre: str, db: Session = Depends(get_db)):
    """
    Devuelve cuántos comentarios positivos/negativos/neutrales ha escrito un usuario concreto.
    """
    resultados = (
        db.query(Feedback.sentimiento, func.count(Feedback.id))
        .filter(Feedback.autor == nombre)
        .group_by(Feedback.sentimiento)
        .all()
    )

    if not resultados:
        raise HTTPException(
            status_code=404, detail=f"No se ha encontrado ningún feedback de {nombre}")

    resumen = {sentimiento: cantidad for sentimiento, cantidad in resultados}
    resumen["total"] = sum(resumen.values())

    return resumen


@router.get("/ranking_usuarios", summary="Usuarios que más feedback han enviado")
async def ranking_por_actividad(db: Session = Depends(get_db)):
    """
    Devuelve un ranking con los usuarios que más comentarios han escrito, en orden descendente.
    """
    resultados = (
        db.query(Feedback.autor, func.count(Feedback.id))
        .group_by(Feedback.autor)
        .order_by(func.count(Feedback.id).desc())
        .all()
    )

    resumen = {autor: cantidad for autor, cantidad in resultados}
    return resumen


@router.get("/ultimos_feedbacks", summary="Últimos feedbacks enviados")
async def ultimos_feedbacks(limit: int = 5, db: Session = Depends(get_db)):
    """
    Devuelve los últimos feedbacks registrados, ordenados por fecha descendente.
    Incluye autor, sentimiento, fecha y comentario.
    """
    resultados = (
        db.query(Feedback)
        .order_by(Feedback.fecha.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "autor": fb.autor,
            "sentimiento": fb.sentimiento,
            "fecha": fb.fecha,
            "comentario": fb.comentario,
        }
        for fb in resultados
    ]


@router.get("/palabras_frecuentes", summary="Devuelve las 10 palabras más comunes")
async def palabras_frecuentes(db: Session = Depends(get_db)):
    """
    Analiza todos los comentarios de feedback y devuelve las 10 palabras
    más repetidas tras limpiar el texto (minúsculas y eliminación de signos).
    """
    stopwords_es = {
        "el", "la", "los", "las", "de", "del", "a", "al", "en", "por", "para",
        "y", "o", "con", "sin", "un", "una", "unos", "unas", "es", "son",
        "que", "como", "más", "muy", "se", "lo", "su", "sus", "ya", "no", "me", "mi", "fue"
    }

    # 1. Obtener todos los comentarios de la base de datos
    resultados = db.query(Feedback).all()

    text_list = []

    # 2. Limpiar cada comentario
    for fb in resultados:
        # Convertir a minúsculas
        texto = fb.comentario.lower()

        # Eliminar signos, dejando solo letras, números y espacios
        texto = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]", "", texto)

        # Eliminar espacios al inicio y final
        texto = texto.strip()

        # Añadir a la lista de textos
        text_list.append(texto)

    # 3. Unir todos los comentarios y separarlos en palabras individuales
    todas_las_palabras = " ".join(text_list).split()

    # filtra las "palabras" que no queremos que cuenten
    palabras_filtradas = [
        palabra for palabra in todas_las_palabras if palabra not in stopwords_es
    ]

    # 4. Contar ocurrencias de cada palabra
    conteo = Counter(palabras_filtradas)

    # 5. Obtener las 10 más comunes
    palabras_mas_comunes = conteo.most_common(10)

    # Convertimos a lista de diccionarios para un JSON más legible
    resultado_json = [
        {"palabra": palabra, "frecuencia": cantidad}
        for palabra, cantidad in palabras_mas_comunes
    ]

    return resultado_json


@router.get("/feedback_extremos", summary="Devuelve el feedback más corto y más largo")
async def feedback_extremos(db: Session = Depends(get_db)):
    resultados = db.query(Feedback).all()

    data = [{
        "id": fb.id,
        "autor": fb.autor,
        "comentario": fb.comentario,
        "fecha": fb.fecha,
        "longitud": len(fb.comentario)
    } for fb in resultados]

    df = pd.DataFrame(data)

    if df.empty:
        raise HTTPException(status_code=401, detail=f"No hay feedbacks")

    # Obtener el más corto y el más largo
    feedback_corto = df.loc[df["longitud"].idxmin()].to_dict()
    feedback_largo = df.loc[df["longitud"].idxmax()].to_dict()

    return {
        "más_corto": feedback_corto,
        "más_largo": feedback_largo
    }


@router.get("/feedback_por_fecha", summary="Distribución de feedbacks por fecha")
async def feedback_por_fecha(db: Session = Depends(get_db)):
    """
    Devuelve un resumen de cuántos feedbacks se han recibido por día.
    Útil para detectar picos o patrones en la actividad.
    """
    resultados = db.query(Feedback).all()

    data = [{
        "fecha": fb.fecha.date()
    } for fb in resultados]

    df = pd.DataFrame(data)

    conteo_por_fecha = df.groupby("fecha").size().reset_index(name="cantidad")

    resultado = conteo_por_fecha.to_dict(orient="records")

    return resultado
