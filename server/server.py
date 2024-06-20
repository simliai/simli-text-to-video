# This acts as that generates audio and sends the stream to the frontend client
# The audio is generated using the Play.ht API and then streamed to the client using websockets
# It uses FFMPEG to convert the audio stream to the PCM format


import asyncio
import logging
import aiohttp
from fastapi import FastAPI , WebSocket, WebSocketDisconnect
import granian
from granian import Granian
from granian.constants import Interfaces
import subprocess
app = FastAPI()
import uvicorn

import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Play.ht API key and user ID
playHT_API_KEY = os.getenv('playHT_API_KEY')
playHT_USER_ID = os.getenv('playHT_USER_ID')

# Generate audio using playHT and encode it using FFMPEG
async def generateAndEncode(websocket):
    command = """
    curl -X POST \
        -H "Content-Type: application/json" \
        -H "accept: audio/mpeg" \
        -H "AUTHORIZATION: playHT_API_KEY" \
        -H "X-USER-ID: playHT_USER_ID" \
        -d '{"text": "Hello from a realistic voice.","voice": "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json","output_format": "mp3"}' \
        "https://api.play.ht/api/v2/tts/stream" | ffmpeg \
        -nostdin \
        -v error \
        -i pipe:0 \
        -f s16le \
        -acodec pcm_s16le \
        -ar 16000 \
        -ac 1 pipe:1
    """
    command = command.replace("playHT_API_KEY", playHT_API_KEY)
    command = command.replace("playHT_USER_ID", playHT_USER_ID)

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
    )
    print("FFMPEG STARTED")
    sendTask = asyncio.create_task(send(websocket, process))
    await sendTask

@app.websocket("/audio")
async def audio_stream(websocket: WebSocket):
    logger.info("Audio WebSocket connection established")
    await websocket.accept()
    try:
        await generateAndEncode(websocket)
    except WebSocketDisconnect:
        logger.info("Audio WebSocket disconnected")
    except Exception as e:
        logger.exception("Unexpected error occurred in audio streaming")

# Send the audio stream to the client
async def send(
    websocket, process: asyncio.subprocess.Process
):
    print("SENDING")
    while True:
        if process.stdout is None:
            print("NO STDOUT")
            break
        data = await process.stdout.read(4096)
        if not data or len(data) == 0:
            print("NO STDOUT")
            break
        print("Sending bytes:",len(data))
        await websocket.send_bytes(data)
    print("Closing socket")
    process.kill()
    await process.wait()
    await websocket.close()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("server:app", port=9000, log_level="info")
