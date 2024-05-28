from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import re
from youtube_transcript_api import YouTubeTranscriptApi
from openai_api.openai_utils import get_summary
import requests
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')  # Reemplaza esto con el ID de la voz que deseas usar
CHUNK_SIZE = 1024

class YouTubeScraper:
    def __init__(self, url):
        self.url = url
        self.video_id = self.extract_video_id(url)

    def extract_video_id(self, url):
        video_id = None
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        match = re.match(youtube_regex, url)
        if match:
            video_id = match.group(6)
        if video_id:
            return video_id
        else:
            raise ValueError("URL de YouTube no válida")

    def get_transcript(self, languages=['es']):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(self.video_id, languages)
            transcript_text = " ".join([entry['text'] for entry in transcript])
            return transcript_text
        except Exception as e:
            print(f"Error al obtener la transcripción en los idiomas {languages}: {str(e)}")
            return None

def generate_audio(text, api_key, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.6
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        os.makedirs("static/audio", exist_ok=True)
        audio_file_path = "static/audio/generated_audio.mp3"
        with open(audio_file_path, "wb") as audio_file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    audio_file.write(chunk)
        return audio_file_path
    else:
        raise Exception(f"Error al generar audio: {response.text}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            scraper = YouTubeScraper(url)
            transcript = scraper.get_transcript()
            if transcript:
                summary = get_summary(transcript)
                audio_file_path = generate_audio(summary, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID)
                return render_template('index.html', transcript=transcript, summary=summary, audio_file_path=audio_file_path)
            else:
                flash("No se pudo obtener la transcripción.", "danger")
        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
