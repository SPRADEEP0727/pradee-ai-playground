"""
A2A protocol demo — the CLIENT side.

Discovers the remote agent via its Agent Card, sends it a message using the
official `a2a-sdk`, and prints the "Hello, World!" reply.

Run:  (start agent_server.py first, then)  python agent_client.py
"""

import asyncio
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)

BASE_URL = "http://localhost:9999"


async def main() -> None:
    async with httpx.AsyncClient() as http:
        # 1) Discover the agent by fetching its Agent Card.
        resolver = A2ACardResolver(httpx_client=http, base_url=BASE_URL)
        agent_card = await resolver.get_agent_card()
        print(f"Discovered agent: {agent_card.name}")

        # 2) Build a client bound to that agent.
        client = A2AClient(httpx_client=http, agent_card=agent_card)

        # 3) Send a message.
        request = SendMessageRequest(
            id=uuid4().hex,
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    message_id=uuid4().hex,
                    parts=[Part(root=TextPart(text="hi"))],
                )
            ),
        )
        response = await client.send_message(request)

        # 4) Print the agent's reply text.
        reply = response.root.result.parts[0].root.text
        print(f"Agent replied: {reply}")


if __name__ == "__main__":
    asyncio.run(main())
