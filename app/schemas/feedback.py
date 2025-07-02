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