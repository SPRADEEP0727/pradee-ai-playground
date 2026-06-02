"""
A2A protocol demo — the SERVER side (a remote agent).

A minimal "Hello World" agent exposed over the Agent-to-Agent (A2A)
protocol using the official `a2a-sdk`. It publishes an Agent Card at
http://localhost:9999/.well-known/agent-card.json and replies "Hello, World!"
to every message.

Run:  python agent_server.py
"""

import uvicorn

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils import new_agent_text_message


class HelloWorldExecutor(AgentExecutor):
    """The agent logic. A2A calls execute() for every incoming message."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Reply with a fixed greeting, sent back as an agent message.
        await event_queue.enqueue_event(new_agent_text_message("Hello, World!"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")


def build_agent_card() -> AgentCard:
    """The Agent Card is the agent's public 'business card' that clients discover."""
    skill = AgentSkill(
        id="hello",
        name="Hello World",
        description="Returns a Hello World greeting.",
        tags=["hello", "demo"],
        examples=["hi", "hello"],
    )

    return AgentCard(
        name="Hello World Agent",
        description="A minimal A2A agent that says Hello, World!",
        url="http://localhost:9999/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )


def main() -> None:
    handler = DefaultRequestHandler(
        agent_executor=HelloWorldExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=build_agent_card(),
        http_handler=handler,
    )

    print("A2A Hello World agent running at http://localhost:9999")
    uvicorn.run(server.build(), host="0.0.0.0", port=9999)


if __name__ == "__main__":
    main()
