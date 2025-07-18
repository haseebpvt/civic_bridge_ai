# others/transcribe.py

import io

import httpx
from pydub import AudioSegment

# ——— Credentials from your example ———
API_KEY = "PXaShdqa7vXgXMyF9wtMGsVKeXGAoSHGG9l5s_MsNuVm"
SERVICE_URL = "https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/9dc09ef8-be44-4a66-a529-15f13aa79333"

# ——— IBM endpoints ———
_IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
_STT_RECOGNIZE = f"{SERVICE_URL}/v1/recognize"


async def transcribe_audio_bytes(
        audio_bytes: bytes,
        model: str = "en-US_BroadbandModel"
) -> str:
    """
    Convert arbitrary audio bytes to WAV, send to IBM Watsonx Speech-to-Text,
    and return the full transcript.

    :param audio_bytes: Raw audio payload (e.g. from Twilio).
    :param model: IBM STT model name.
    :return: Combined transcript string.
    """

    # 1) Convert any format ↦ 16 kHz mono WAV
    segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
    segment = segment.set_frame_rate(16000).set_channels(1)
    wav_io = io.BytesIO()
    segment.export(wav_io, format="wav")
    wav_bytes = wav_io.getvalue()

    # 2) Fetch IAM token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            _IAM_TOKEN_URL,
            data={
                "apikey": API_KEY,
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]

        # 3) Send WAV to STT
        stt_resp = await client.post(
            _STT_RECOGNIZE,
            params={"model": model},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "audio/wav"
            },
            content=wav_bytes
        )
        stt_resp.raise_for_status()
        result = stt_resp.json()

    # 4) Extract & join transcripts
    transcripts = [
        r["alternatives"][0]["transcript"].strip()
        for r in result.get("results", [])
    ]
    return " ".join(transcripts)
