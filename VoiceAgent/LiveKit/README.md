# LiveKit Setup

Steps to install and run a LiveKit voice agent locally.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.10+
- VS Code (or any editor)

## Installation Steps

### 1) Install Docker Desktop
Download and install Docker Desktop for your OS.

### 2) Open Docker Desktop
Make sure Docker is running before continuing.

### 3) Create the project folder
Create a folder named `LiveKit` on your machine and open it in VS Code.
(In this repo it lives at `VoiceAgent/LiveKit`.)

### 4) Open a terminal in VS Code
Use `cmd` on Windows or `bash` on macOS.

### 5) Pull the LiveKit generator image
```bash
docker pull livekit/generate
```

### 6) Pull the LiveKit server image
```bash
docker pull livekit/livekit-server
```

#### 6.i) Fallback (Optional) — run the LiveKit server locally
```bash
docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp livekit/livekit-server /livekit-server --dev
```

### 7) Open a second terminal in VS Code
Leave the server running in the first terminal and open another `cmd` / `bash` tab.

### 8) Create and activate a Python virtual environment

**Windows (cmd):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 9) Install the LiveKit dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `livekit-agents[openai]~=1.2`
- `livekit-plugins-noise-cancellation~=0.2`
- `livekit-plugins-silero~=1.2` (VAD — required because OpenAI STT is non-streaming)
- `python-dotenv`

### 10) Create your agent
A demo `agent.py` is already included in this folder — a friendly classroom
assistant that uses OpenAI for STT, LLM, and TTS, Silero VAD for turn
detection, plus LiveKit's noise cancellation. Read through it, then customize
the `instructions` string in `ClassroomAssistant` for your lesson.

> **Why Silero VAD?** OpenAI's STT models are non-streaming, so the agent
> needs a Voice Activity Detector to chunk microphone audio into utterances.
> Without it you'll see `RuntimeError: The STT ... does not support streaming,
> add a VAD ...`.

### 11) Run the agent
Easiest way to demo — talk to it right in the terminal:
```bash
python agent.py console
```
Or connect it to a LiveKit room (uses `.env` for credentials):
```bash
python agent.py dev
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your real keys. Do **NOT** commit `.env`.

```
OPENAI_API_KEY=sk-your-openai-key
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

## Notes

- Keep Docker Desktop running while developing locally.
- The dev server exposes ports `7880` (HTTP/WS), `7881` (TCP), and `7882/udp` (media).
- Always activate the venv before running `pip install` or `python agent.py`.
