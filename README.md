# Gestor de Feedback Inteligente

## Descripción del proyecto

**Gestor de Feedback Inteligente** es una API desarrollada con FastAPI que permite recibir, analizar y consultar feedback de usuarios o empleados, integrando análisis de sentimiento, clasificación temática y generación de respuestas automáticas mediante IA (OpenAI). Incluye autenticación, métricas avanzadas y funcionalidades de filtrado y análisis para recursos humanos o equipos de experiencia del empleado.

---

## Estructura de archivos

```
gestor_feedback/
│
├── app/
│   ├── ai/                  # Integración y lógica de análisis con OpenAI
│   ├── analytics/           # Servicios de estadísticas y métricas
│   ├── api/                 # Endpoints principales: feedback, métricas, auth
│   ├── db/                  # Configuración y utilidades de base de datos
│   ├── models/              # Modelos ORM (SQLAlchemy)
│   ├── schemas/             # Esquemas Pydantic para validación
│   ├── services/            # Lógica de negocio (servicios)
│   ├── test/                # Tests automáticos (pytest)
│   ├── utils/               # Utilidades y dependencias comunes
│   └── main.py              # Punto de entrada de la aplicación FastAPI
│
├── requirements.txt         # Dependencias del proyecto
└── .gitignore               # Archivos y carpetas ignorados por git
```

---

## Instalación y configuración

1. **Clona el repositorio:**
   ```bash
   git clone <URL_DEL_REPO>
   cd gestor_feedback
   ```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # En Windows
   source .venv/bin/activate  # En Linux/Mac
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno:**
   - Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
     ```
     OPENAI_API_KEY=tu_clave_de_openai
     ```
   - Si usas una base de datos diferente a la predeterminada, añade también la cadena de conexión correspondiente.

5. **Inicializa la base de datos:**
   - La base de datos se inicializa automáticamente al arrancar la app, creando las tablas si no existen.

---

## Uso y ejemplos

### Arrancar el servidor de desarrollo

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: [http://localhost:8000](http://localhost:8000)

### Endpoints principales

- **Autenticación**
  - `POST /auth/register` — Registro de usuario
  - `POST /auth/login` — Login y obtención de token JWT
  - `GET /auth/me` — Información del usuario autenticado

- **Feedback**
  - `POST /feedback/` — Crear feedback (analiza automáticamente con IA)
  - `GET /feedback/` — Listar todos los feedbacks
  - `GET /feedback/{id}` — Obtener feedback por ID
  - `PATCH /feedback/{id}` — Actualizar feedback parcialmente
  - `DELETE /feedback/{id}` — Eliminar feedback
  - `GET /feedback/filtrados` — Filtrar feedbacks por autor, fecha, sentimiento, urgencia
  - Funciones IA: responder, sugerir mejoras, detectar toxicidad, clasificar urgencia, analizar evolución de sentimiento

- **Métricas**
  - `GET /metrics/resumen` — Resumen general de sentimientos (IA)
  - `GET /metrics/general` — Cantidad de feedbacks por sentimiento
  - `GET /metrics/por_usuario?nombre=...` — Resumen de sentimientos por usuario
  - `GET /metrics/ranking_usuarios` — Ranking de usuarios más activos
  - `GET /metrics/ultimos_feedbacks` — Últimos feedbacks enviados
  - `GET /metrics/palabras_frecuentes` — Palabras más comunes en los comentarios
  - `GET /metrics/feedback_extremos` — Feedback más corto y más largo

### Ejemplo de petición para crear feedback

```json
POST /feedback/
{
  "autor": "Juan",
  "comentario": "El ambiente laboral ha mejorado mucho este mes."
}
```

Respuesta:
```json
{
  "id": 1,
  "autor": "Juan",
  "comentario": "El ambiente laboral ha mejorado mucho este mes.",
  "sentimiento": "positivo",
  "etiquetas": ["ambiente", "mejora"],
  "resumen": "El ambiente laboral ha mejorado.",
  "fecha": "2024-06-01T12:34:56"
}
```

---

## Tecnologías utilizadas

- **FastAPI** — Framework principal para la API
- **Pydantic** — Validación y serialización de datos
- **SQLAlchemy** — ORM para la base de datos
- **Uvicorn** — Servidor ASGI para desarrollo y producción
- **OpenAI** — Análisis de sentimiento, generación de respuestas y sugerencias
- **Pandas** — Procesamiento de datos para métricas
- **pytest** y **httpx** — Testing automatizado
- **python-dotenv** — Gestión de variables de entorno

---

## Scripts disponibles

- **Arrancar el servidor de desarrollo:**
  ```bash
  uvicorn app.main:app --reload
  ```

- **Ejecutar los tests automáticos:**
  ```bash
  pytest app/test/
  ``` 