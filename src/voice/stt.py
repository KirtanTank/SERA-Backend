import os
from openai import OpenAI
import base64
import tempfile

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def speech_to_text(audio_base64: str) -> str:
    # Decode base64 audio
    audio_bytes = base64.b64decode(audio_base64)

    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp.flush()

        transcription = client.audio.transcriptions.create(
            file=open(tmp.name, "rb"),
            model="whisper-1"
        )

    return transcription.text
