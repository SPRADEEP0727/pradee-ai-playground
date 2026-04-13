"""
Main entry point for Adaptive RAG.
Run: python main.py

This file handles:
1. Suppressing known warnings (Pydantic V1 + Python 3.14)
2. Loading environment variables (.env file with API keys)
3. Mapping env var names (SERP_API_KEY → SERPAPI_API_KEY)
4. Initializing the LLM and embeddings
5. Running the interactive question-answer loop
"""

import warnings
# Suppress Pydantic V1 deprecation warning (known issue with Python 3.14 + LangChain)
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")

import os
from dotenv import load_dotenv

# ── Load API keys from .env.example file ──
# load_dotenv() reads the file and sets the values as environment variables
# so that OpenAI and SerpAPI can find their API keys automatically
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.example")
load_dotenv(env_path)

# ── Fix SerpAPI env var name ──
# Our .env uses SERP_API_KEY, but the serpapi library expects SERPAPI_API_KEY
# This maps one to the other so both work
if os.getenv("SERP_API_KEY") and not os.getenv("SERPAPI_API_KEY"):
    os.environ["SERPAPI_API_KEY"] = os.getenv("SERP_API_KEY")

# ── Initialize the adaptive RAG system ──
# IMPORTANT: import AFTER load_dotenv() so API keys are available
from adaptive_rag import init, adaptive_rag
init()  # Creates the LLM and embedding model instances


def main():
    """Interactive loop: ask questions, get adaptive RAG answers."""

    print("\n" + "=" * 60)
    print("  ADAPTIVE RAG — Interactive Mode")
    print("  Type your question and press Enter.")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    # Keep asking for questions until user types quit/exit
    while True:
        print()
        query = input("Your question: ").strip()

        # Skip empty input
        if not query:
            continue

        # Exit commands
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # Run the full Adaptive RAG pipeline:
        # Route → Retrieve → Check Relevance → Fallback if needed → Generate Answer
        adaptive_rag(query)


if __name__ == "__main__":
    main()
