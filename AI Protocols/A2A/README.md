# A2A Protocol — Hello World Demo

A minimal demonstration of the **Agent-to-Agent (A2A)** protocol using the
official [`a2a-sdk`](https://pypi.org/project/a2a-sdk/).

A client **discovers** a remote agent via its Agent Card, **sends** it a message,
and the agent replies **"Hello, World!"** — the full A2A loop.

## Files

| File | Role | What it does |
|------|------|--------------|
| `agent_server.py` | Remote agent | Exposes a Hello World agent over HTTP and publishes an Agent Card |
| `agent_client.py` | Caller | Discovers the agent and sends it a message |

## Prerequisites

- Python 3.10+
- Two terminals (one for the server, one for the client)

## Setup

### 1. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If activation is blocked, allow scripts for the current user once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install "a2a-sdk[http-server]==0.3.26" uvicorn httpx
```

> **Why the pinned version?** `a2a-sdk` 1.x is a major rewrite that removed the
> simple `A2AStarletteApplication` / `A2AClient` API this demo uses (and conflicts
> with `fastapi`'s `starlette` pin). The `0.3.x` series is the last with the
> simple, well-documented API.

## Run

> Activate the venv (step 1) in **both** terminals before running.

### Terminal 1 — start the agent

```bash
python agent_server.py
```

You should see:

```
A2A Hello World agent running at http://localhost:9999
```

The Agent Card is now discoverable at:
<http://localhost:9999/.well-known/agent-card.json>

### Terminal 2 — run the client

```bash
python agent_client.py
```

Expected output:

```
Discovered agent: Hello World Agent
Agent replied: Hello, World!
```

## How it works

1. **Agent Card** — the server publishes a JSON "business card" describing its
   name, skills, and capabilities at `/.well-known/agent-card.json`.
2. **Discovery** — the client uses `A2ACardResolver` to fetch that card.
3. **Messaging** — the client uses `A2AClient.send_message()` to send an A2A
   `Message`; the server's `HelloWorldExecutor.execute()` handles it and replies.

## Troubleshooting

- **`Connection refused`** — make sure the server (Terminal 1) is running first.
- **`error while attempting to bind on address ('0.0.0.0', 9999)`** — port 9999
  is already in use (e.g. an old server still running). Stop it and retry.
- **`ModuleNotFoundError: No module named 'a2a.server.apps'`** — you have
  `a2a-sdk` 1.x installed. Pin to `0.3.26` (see Setup).
- **`DeprecationWarning: A2AClient is deprecated`** — harmless on `0.3.x`; the
  client still works. It is the intended simple API for this demo.
