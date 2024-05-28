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
                {"role": "user", "content": f"Captures la idea general del siguiente texto y genera contenido para ser utilizado en un video, debes mantener el tono y la idea general, no hagas introducciones ve directo al contenido, no uses llaves con explicaciones, tu objetivo es generar la narración, no empices o digas cosas como, en el Texto..., sino ve directo a hablar sobre el contenido, debe parecer que es contenido propio y no que estas analizando, el texto es:\n\n{text}"}
            ],
            max_tokens=400,
            temperature=0.7,
        )
        summary = response.choices[0]['message']['content'].strip()
        return summary
    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        return None
    except openai.RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
        return None
    except openai.APIError as e:
        print("An API error occurred")
        print(e.status_code)
        print(e.response)
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return None
