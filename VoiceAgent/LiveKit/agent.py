"""
LiveKit Voice Agent — Classroom Demo
====================================

A minimal voice agent built with the LiveKit Agents framework.

It connects to a LiveKit room, listens to the user's microphone, transcribes
speech with OpenAI's STT, generates a response with GPT, speaks it back via
OpenAI TTS, and applies background-noise cancellation along the way.

Run modes:
    python agent.py console     # talk to the agent right in the terminal
    python agent.py dev         # connect to a LiveKit room (uses .env)
    python agent.py start       # production worker mode

Environment variables (put these in a .env file beside this script):
    OPENAI_API_KEY=sk-...
    LIVEKIT_URL=ws://localhost:7880
    LIVEKIT_API_KEY=devkey
    LIVEKIT_API_SECRET=secret
"""

from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import noise_cancellation, openai, silero

load_dotenv()


class ClassroomAssistant(Agent):
    """A friendly teaching assistant the students can talk to."""

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a friendly classroom assistant helping students learn "
                "about LiveKit and voice agents. Keep answers short, clear, and "
                "encouraging. If a student asks something off-topic, gently "
                "steer them back to the lesson."
            )
        )


async def entrypoint(ctx: agents.JobContext) -> None:
    session = AgentSession(
        stt=openai.STT(model="gpt-4o-mini-transcribe"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=ClassroomAssistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions=(
            "Greet the student warmly, introduce yourself as their LiveKit "
            "classroom assistant, and ask what they'd like to learn today."
        )
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
