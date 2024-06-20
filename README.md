

# Simli Text To Video Sample Repo

This sample repository is meant as a guiding code in how to create secure a text to video application.
There is a fastapi backend server that generates the audio using PlayHT but any audio provider can be used. The audio stream is passed to the frontend using a websocket endpoint. The stream is subsequently sent to **api.simli.ai**

# How to run

## Setup

Install node dependencies
```
npm install
```

Setup python environment

```
cd server
python3 -m venv .venv
source .venv/bin/activate
```
Install dependencies
```
pip3 install -r requirements
```

## Environment variables

Add the following environment variables in the given `.env` file

```
NEXT_PUBLIC_SIMLI_API_KEY=""
playHT_API_KEY = ""
playHT_USER_ID = ""
```

Signup at [Play HT](https://play.ht/) for playHT_API_KEY and playHT_USER_ID

Signup at [Simli.com](https://www.simli.com/) for Simli API Key

## Running the Project

Run the frontend in one terminal

```
npm run build
npm run dev
```
Run the server in one terminal

```
python3 server/server.py
```

**NOTES**

The `server.py` reads from .env in the root directory, so make sure to run it from there.
