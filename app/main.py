from fastapi import FastAPI
from app.api import feedback, metrics, auth
from app.db.init_db import init_db

# deactivate
# .venv\Scripts\activate
# uvicorn app.main:app --reload


app = FastAPI(
    title="Gestor de Feedback Inteligente",
    description="API para recibir, analizar y consultar feedback con IA."
)

app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

init_db()  # Crea la tabla si no existe

@app.get("/")
async def root():
    return {"mensaje": "Bienvenido al Gestor de Feedback Inteligente con FastAPI 🚀"}