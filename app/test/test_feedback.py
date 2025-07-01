import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app  

# Creamos el cliente de prueba con la app
client = TestClient(app)

def test_crear_feedback():
    """
    Test básico para comprobar que se puede crear un feedback correctamente.
    """
    payload = {
        "autor": "TestUser",
        "comentario": "Este es un comentario de prueba para verificar el endpoint"
        # No incluimos fecha, para que use la actual automáticamente
    }

    response = client.post("/feedback/", json=payload)

    # Comprobamos que la respuesta es exitosa
    assert response.status_code == 200

    # Parseamos el JSON de respuesta
    data = response.json()

    # Comprobamos que los campos esperados existen en la respuesta
    assert "id" in data
    assert data["autor"] == "TestUser"
    assert "sentimiento" in data
    assert "resumen" in data
    assert "etiquetas" in data


