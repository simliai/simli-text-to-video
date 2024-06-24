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
characterVoice = os.getenv('characterVoice')

# Generate audio using playHT and encode it using FFMPEG
async def generateAndEncode(websocket, sentence):
    url = "https://api.play.ht/api/v2/tts/stream"
    headers = {
        "Content-Type": "application/json",
        "accept": "audio/mpeg",
        "AUTHORIZATION": playHT_API_KEY,
        "X-USER-ID": playHT_USER_ID,
    }
    data = {
        "text": sentence,
        "voice": characterVoice,
        "output_format": "mp3"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                print(f"Request failed with status: {response.status}")
                return

            # Create the ffmpeg process
            ffmpeg_process = await asyncio.create_subprocess_exec(
                'ffmpeg',
                '-nostdin',
                '-v', 'error',
                '-i', 'pipe:0',
                '-f', 's16le',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                'pipe:1',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE
            )

            # Stream the response content to ffmpeg stdin
            async for chunk in response.content.iter_chunked(4096):
                ffmpeg_process.stdin.write(chunk)
            await ffmpeg_process.stdin.drain()
                # Write to file
            ffmpeg_process.stdin.close()
            await ffmpeg_process.wait()
            # Close ffmpeg stdin and wait for process to complete
            print("FFMPEG STARTED")
            sendTask = asyncio.create_task(send(websocket, ffmpeg_process))
            await sendTask


@app.websocket("/audio")
async def audio_stream(websocket: WebSocket):
    logger.info("Audio WebSocket connection established")
    await websocket.accept()
    try:
        sentence = await websocket.receive_text()
        await generateAndEncode(websocket, sentence)
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

    silence = b'\x00' * 4096  # 1024 bytes of silence
    try:
        while True:

            await websocket.send_bytes(silence)
            # How long to sleep
            # Bytes per second=Sample rate × Bytes per sample × Number of channels
            # Duration in seconds= Number of bytes / bytes per second

            await asyncio.sleep(0.128)
    except:
        print("Socket closed")
    
    try:
        process.kill()
    except:
        print("Process already killed")
    
    print("Closing socket")
    
    await process.wait()
    await websocket.close()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("server:app", port=9000, log_level="info")
