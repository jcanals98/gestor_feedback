from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime

class FeedbackIn(BaseModel):
    autor: str
    comentario: str
    fecha: Optional[datetime] = None 

class FeedbackOut(BaseModel):
    sentimiento: str
    etiquetas: List[datetime]
    resumen: str

class FeedbackUpdate(BaseModel):
    autor: Optional[str] = None
    comentario: Optional[str] = None
    fecha: Optional[datetime] = None
    sentimiento: Optional[str] = None
    etiquetas: Optional[List[str]] = None
    resumen: Optional[str] = None
    respuesta: Optional[str] = None
    sugerencia: Optional[str] = None
    urgencia: Optional[str] = None

class FeedbackDB(BaseModel):
    id: int
    autor: str
    comentario: str
    fecha: datetime
    sentimiento: str
    etiquetas: List[str]
    resumen: str
    respuesta: Optional[str]
    sugerencia: Optional[str]
    urgencia: Optional[str]

    @field_validator("etiquetas", mode="before")
    def convertir_etiquetas(cls, v):
        if isinstance(v, str):
            return [e.strip() for e in v.split(",")]
        return v

  
    model_config = ConfigDict(from_attributes=True)# Esto es necesario para usar objetos SQLAlchemy como respuesta