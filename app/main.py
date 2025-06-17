from fastapi import FastAPI

app = FastAPI(
    title="Gestor de Feedback Inteligente",
    description="API para recibir, analizar y consultar feedback con IA."
)

@app.get("/")
async def root():
    return {"mensaje": "Bienvenido al Gestor de Feedback Inteligente con FastAPI 🚀"}