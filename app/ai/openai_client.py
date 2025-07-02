import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Cargar la API key desde .env y crear el cliente de OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Función genérica para generar respuestas con un prompt y parámetros configurables
def generar_respuesta_openai(
    system_content: str,
    user_prompt: str,
    temperature: float = 0.5,
    max_tokens: int = 200
) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()


# Análisis completo del comentario: sentimiento, etiquetas y resumen
def analizar_feedback_con_ia(comentario: str) -> dict:
    prompt = f"""
    Analiza el siguiente comentario de un empleado y devuelve:

    1. Sentimiento general: elige solo entre positivo, negativo o neutro.
    2. Dos o tres etiquetas temáticas que resuman los temas clave del comentario.
    3. Un resumen breve y neutro del comentario en una sola frase.

    Comentario: {comentario}

    Devuelve solo un JSON válido con esta estructura:
    {{
      "sentimiento": "positivo | negativo | neutro",
      "etiquetas": ["etiqueta1", "etiqueta2"],
      "resumen": "frase resumen del comentario"
    }}
    """
    system = "Eres un analista de RRHH que entiende comentarios humanos."
    contenido = generar_respuesta_openai(system, prompt, temperature=0.4)

    try:
        return json.loads(contenido)
    except Exception:
        return {
            "sentimiento": "neutro",
            "etiquetas": [],
            "resumen": "No se pudo procesar el comentario."
        }


# Genera una respuesta profesional a un comentario negativo
def generar_respuesta_educada(comentario: str) -> str:
    prompt = f"""
    Eres un asistente profesional de RRHH. Responde con educación y empatía a este comentario negativo:

    Comentario del empleado:
    {comentario}
    """
    system = "Eres especialista en tratar temas delicados con educación y empatía en un departamento de atención al cliente."
    return generar_respuesta_openai(system, prompt, temperature=0.5)


# Propone una mejora basada en el comentario del empleado
def generar_sugerencia_para_comentario(comentario: str) -> str:
    prompt = f"""
    Comentario del empleado:
    {comentario}

    Propón una sugerencia útil que la empresa pueda aplicar. Devuelve solo una frase con la sugerencia.
    """
    system = "Eres un consultor experto en gestión de equipos y experiencia del empleado. Tu tarea es proponer una mejora concreta a partir del comentario."
    return generar_respuesta_openai(system, prompt, temperature=0.7)


# Detecta si el comentario tiene tono tóxico y explica por qué
def analizar_toxicidad_comentario(comentario: str) -> dict:
    prompt = f"""
    Comentario del empleado:
    \"{comentario}\"

    Analiza si el comentario contiene lenguaje tóxico, agresivo o inapropiado.
    Devuelve una respuesta en formato JSON con los siguientes campos:
    - toxico: true o false
    - razon: una frase corta explicando por qué es tóxico o no
    """
    system = "Eres un experto en análisis de lenguaje y recursos humanos. Tu trabajo es detectar si un comentario es tóxico y explicar por qué."
    contenido = generar_respuesta_openai(system, prompt, temperature=0.3)

    try:
        return json.loads(contenido)
    except Exception:
        return {
            "toxico": None,
            "razon": f"No se pudo interpretar correctamente la respuesta: {contenido}"
        }


# Clasifica la urgencia del comentario según su contenido
def clasificar_nivel_urgencia(comentario: str) -> str:
    prompt = f"""
    Clasifica este comentario de un empleado según su nivel de urgencia para que el equipo de RRHH actúe:

    Comentario: {comentario}

    Categorías posibles: urgente, normal, baja.

    Devuelve solo una palabra: urgente, normal o baja.
    """
    system = "Eres un experto en RRHH que evalúa la urgencia de comentarios internos."
    contenido = generar_respuesta_openai(system, prompt, temperature=0.3)
    return contenido.strip().lower()


# Evalúa si ha habido un cambio de actitud en una serie de sentimientos
def detectar_cambio_de_sentimiento(historial: list[str]) -> str:
    prompt = f"""
    Analiza esta secuencia de sentimientos expresados por un mismo empleado a lo largo del tiempo:

    Historial: {historial}

    ¿Detectas algún cambio relevante en su actitud?

    Devuelve solo una frase clara y directa sobre si ha mejorado, empeorado o si su actitud es estable.
    """
    system = "Eres un experto en analizar patrones emocionales en comentarios de empleados."
    return generar_respuesta_openai(system, prompt, temperature=0.4)
