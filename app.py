import os
import httpx
from fastapi import FastAPI, Form, Response
from pydub import AudioSegment
from pydub.utils import which
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from others.transcribe import transcribe_audio_bytes
from watson_orchestrate_api import send_to_watson

# Load environment variables
load_dotenv()

# Ensure pydub can find your ffmpeg/ffprobe binaries
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError("Twilio credentials not found in environment variables. Please check your .env file.")

app = FastAPI()


@app.post("/whatsapp")
async def whatsapp_message(
        incoming_text: str = Form(..., alias="Body"),
        num_media: int = Form(0, alias="NumMedia"),
        media_url0: str = Form(None, alias="MediaUrl0"),
        media_type0: str = Form(None, alias="MediaContentType0"),
):
    resp = MessagingResponse()

    if num_media > 0:
        if media_type0.startswith("audio"):
            # Download the media, following 307 redirects
            async with httpx.AsyncClient(
                    auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                    follow_redirects=True,
            ) as client:
                media_resp = await client.get(media_url0)
                if media_resp.status_code != 200:
                    resp.message(f"Failed to fetch media: HTTP {media_resp.status_code}")
                    return Response(content=str(resp), media_type="application/xml")

                audio_bytes = media_resp.content

            transcription = await transcribe_audio_bytes(audio_bytes=audio_bytes)

            # Send transcription to Watson Orchestrate API
            watson_response = send_to_watson(transcription)

            if watson_response:
                resp.message(f"Transcription: {transcription}\n\nResponse: {watson_response}")
            else:
                resp.message(f"Transcription: {transcription}\n\nError: Could not process with Watson Orchestrate")
        elif media_type0.startswith("image"):
            resp.message("Image received")
    else:
        resp.message(f"Welcome to CivicBridge AI! If you have any questions or encounter any issues, feel free to let me know.")

    return Response(content=str(resp), media_type="application/xml")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("app:app", host="localhost", port=8000)
