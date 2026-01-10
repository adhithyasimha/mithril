import os
import json
import base64
import asyncio
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client
from dotenv import load_dotenv
import uvicorn
from google.cloud import speech
from google.cloud import texttospeech
import google.generativeai as genai

# --------------------------------------------------
# ENV + CONFIG
# --------------------------------------------------
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
NGROK_URL = os.getenv("NGROK_URL")
PORT = int(os.getenv("PORT", 5050))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

assert all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, NGROK_URL, GEMINI_API_KEY])


speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

app = FastAPI()

@app.get("/")
async def health():
    return {"status": "Gemini Voice Bot Running"}


@app.post("/make-call")
async def make_call(request: Request):
    data = await request.json()
    to_number = data.get("to")

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=to_number,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{NGROK_URL}/outgoing-call"
    )
    return {"call_sid": call.sid}

@app.api_route("/outgoing-call", methods=["GET", "POST"])
async def outgoing_call(request: Request):
    response = VoiceResponse()
    response.say("You are now connected to the AI assistant.")
    connect = Connect()
    connect.stream(url=f"wss://{request.url.hostname}/media-stream")
    response.append(connect)
    return HTMLResponse(str(response), media_type="application/xml")


def gemini_reply(text: str) -> str:
    response = gemini_model.generate_content(text)
    return response.text

def tts_audio(text: str) -> bytes:
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-D"
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MULAW,
        sample_rate_hertz=8000
    )

    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    return response.audio_content

@app.websocket("/media-stream")
async def media_stream(ws: WebSocket):
    await ws.accept()
    print("🎧 Twilio connected")

    audio_queue = asyncio.Queue()

    async def receive_audio():
        try:
            async for msg in ws.iter_text():
                data = json.loads(msg)
                if data["event"] == "media":
                    audio = base64.b64decode(data["media"]["payload"])
                    await audio_queue.put(audio)
        except WebSocketDisconnect:
            pass

    async def process_audio():
        requests = (
            speech.StreamingRecognizeRequest(audio_content=chunk)
            for chunk in iter(audio_queue.get, None)
        )

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MULAW,
            sample_rate_hertz=8000,
            language_code="en-US"
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=False
        )

        responses = speech_client.streaming_recognize(streaming_config, requests)

        for response in responses:
            for result in response.results:
                transcript = result.alternatives[0].transcript
                print(" User:", transcript)

                reply = gemini_reply(transcript)
                print("Gemini:", reply)

                audio = tts_audio(reply)
                payload = base64.b64encode(audio).decode()

                await ws.send_json({
                    "event": "media",
                    "media": {"payload": payload}
                })

    await asyncio.gather(receive_audio(), process_audio())


if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)
