import os
import openai
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


async def analizar_feedback_con_ia(comentario: str) -> dict:
    prompt = f"""
        Analiza el siguiente comentario de un empleado y devuelve:

        1. Sentimiento general: elige solo entre positivo, negativo o neutro.
        2. Dos o tres etiquetas temáticas que resuman los temas clave del comentario. Ejemplos: motivación, equipo, liderazgo, comunicación, salario, carga laboral, crecimiento profesional, etc.
        3. Un resumen breve y neutro del comentario en una sola frase. NO repitas el sentimiento ni etiqueta.

        Comentario: {comentario}

        Devuelve solo un JSON válido con esta estructura:
        {{
        "sentimiento": "positivo | negativo | neutro",
        "etiquetas": ["etiqueta1", "etiqueta2"],
        "resumen": "frase resumen del comentario"
        }}
        """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un analista de RRHH que entiende comentarios humanos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=200
    )

    # Extraer el JSON del contenido
    texto_generado = response.choices[0].message.content.strip()
    try:
        resultado = json.loads(texto_generado)
        print(resultado)
        return resultado
    except Exception:
        return {
            "sentimiento": "neutro",
            "etiquetas": [],
            "resumen": "No se pudo procesar el comentario."
        }


def generar_respuesta_educada(comentario: str) -> str:
    prompt = f"""
        Eres un asistente profesional de RRHH. Responde con educación y empatía a este comentario negativo de un empleado.
        No seas defensivo ni uses lenguaje corporativo vacío. Sé claro, humano y constructivo.

        Comentario del empleado:
        {comentario}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres especializta en tratar temas delicados con mucha educacion y empatia en un departamente de atencion al cliente."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()