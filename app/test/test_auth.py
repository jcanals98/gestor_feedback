import sys
import os
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

usuario_test = str(uuid.uuid4())

# 1. REGISTRO DE USUARIO
def test_register_user():
    # Email aleatorio usando UUID
    payload = {
        "email": f"{usuario_test}@mail.com",
        "password": "123456"
    }

    response = client.post("/auth/register", json=payload)

    # Parseamos el JSON de respuesta
    data = response.json()

    # Verificaciones
    assert response.status_code == 200
    assert "id" in data
    assert "email" in data
    assert "role" in data

 
# 2. LOGIN DE USUARIO
def test_login_user():
    
    # Email aleatorio usando UUID
    payload = {
        "email": f"{usuario_test}@mail.com",
        "password": "123456"
    }

    response = client.post("/auth/login", json=payload)

    # Verificaciones
    assert response.status_code == 200
# 3. OBTENER USUARIO ACTUAL
def test_get_current_user():
    # Paso 1: Login para obtener el token
    payload = {
        "email": f"{usuario_test}@mail.com",
        "password": "123456"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Paso 2: Usar el token en la cabecera Authorization
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Paso 3: Llamar a /auth/me autenticado
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200

    # Validar datos del usuario devuelto
    data = response.json()
    assert "id" in data
    assert data["email"] == f"{usuario_test}@mail.com"
    assert "role" in data
