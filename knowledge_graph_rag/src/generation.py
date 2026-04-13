from openai import AsyncOpenAI
from src.config import OPENAI_API_KEY

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided knowledge graph context.
Use ONLY the facts provided in the context to answer. If the context doesn't contain enough information, say so.
Be concise and accurate."""


async def generate_response(
    query: str,
    context: str,
    model: str = "gpt-4o-mini",
) -> str:
    """Generate a response using the LLM with retrieved context."""
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
