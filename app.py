import io

import httpx
from fastapi import FastAPI, Form, Response
from pydub import AudioSegment
from pydub.utils import which
from twilio.twiml.messaging_response import MessagingResponse

from others.transcribe import transcribe_audio_bytes

# Ensure pydub can find your ffmpeg/ffprobe binaries
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

# Twilio credentials (hard-coded for now)
TWILIO_ACCOUNT_SID = "AC03aa6a3de06a799dc0c5bd2fba664184"
TWILIO_AUTH_TOKEN = "972a5887bf945c2b00147b7fd69daeda"

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
            resp.message(f"Transcription: {transcription}")
        elif media_type0.startswith("image"):
            resp.message("Image received")
    else:
        resp.message(f"The text is: {incoming_text}")

    return Response(content=str(resp), media_type="application/xml")
