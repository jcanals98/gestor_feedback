import sys
import os

# Añade el directorio raíz del proyecto al path para permitir las importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app  # Importamos la instancia de FastAPI

# Cliente de pruebas que simula peticiones HTTP a nuestra API
client = TestClient(app)

def test_resumen_sentimientos_endpoint():
    """
    Testea el endpoint GET /metrics/resumen y valida que:
    - Responde con status 200
    - Contiene claves esperadas en el JSON
    - Incluye métricas de sentimiento con datos numéricos válidos
    """
    # Realiza una petición GET al endpoint
    response = client.get("/metrics/resumen")
    
    # Verifica que la respuesta sea exitosa
    assert response.status_code == 200

    # Convierte la respuesta a JSON
    data = response.json()

    # Verifica que el JSON contenga las claves esperadas
    assert "total_feedbacks" in data
    assert "resumen_por_sentimiento" in data

    # Verifica que cada tipo de sentimiento tenga valores numéricos válidos
    resumen = data["resumen_por_sentimiento"]
    assert resumen["positivo"]["cantidad"] >= 0
    assert resumen["neutro"]["cantidad"] >= 0
    assert resumen["negativo"]["cantidad"] >= 0
