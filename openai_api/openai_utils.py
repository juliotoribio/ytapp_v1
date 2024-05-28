import openai
import os

# Configura tu clave API de OpenAI desde una variable de entorno
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_summary(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente útil que genera contenido para ser usado en videos de 1:30 minutos."},
                {"role": "user", "content": f"Captures la idea general del siguiente texto y genera contenido para ser utilizado en un video, debes mantener el tono y la idea general, no hagas introducciones ve directo al contenido, tampoco uses llaves con explicaciones, tu objetivo es generar la narración, no empices o digas cosas como, en el Texto..., sino ve directo a hablar sobre el contenido, debe parecer que es contenido propio y no que estas analizando, el texto es:\n\n{text}"}
            ],
            max_tokens=400,
            temperature=0.7,
        )
        summary = response.choices[0]['message']['content'].strip()
        return summary
    except openai.error.InvalidRequestError as e:
        if "maximum context length" in str(e):
            print(f"Transcripción demasiado larga para procesar: {e}")
            return None
        else:
            raise e
