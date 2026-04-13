# Knowledge Graph RAG

## What This Project Does

Ask questions about your documents using AI. This system reads text files, builds a **knowledge graph** (a web of connected facts) using AI, and uses that understanding to answer questions accurately. Built with Graphiti (by Zep), Neo4j, and OpenAI.

## Tech Stack

- **Python 3.11+**
- **Graphiti** (`graphiti-core`) by Zep - extracts entities and relationships from text into a knowledge graph
- **Neo4j** - graph database that stores the knowledge graph (runs via Docker)
- **OpenAI** (`gpt-4o-mini`) - LLM for entity extraction during ingestion and answer generation during queries
- **python-dotenv** - loads environment variables from `.env`
- **pydantic** - data validation

## Project Structure

```
knowledge_graph_rag/
├── main.py                  # CLI entry point - run this file
├── README.md                # Beginner-friendly setup and usage guide
├── CLAUDE.md                # Project overview for Claude Code
├── claude_build_prompt.md   # Give this to Claude to rebuild the project from scratch
├── requirements.txt         # Python dependencies
├── .env                     # API keys and Neo4j credentials (not committed)
├── .env.example             # Template for .env
├── data/
│   └── elon_musk.txt        # Sample document about Elon Musk
└── src/
    ├── __init__.py           # Makes src a Python package
    ├── config.py             # Loads settings from .env
    ├── graph_utils.py        # Connects to Neo4j via Graphiti client
    ├── ingestion.py          # Reads documents and builds the knowledge graph
    ├── retrieval.py          # Searches the graph and formats context for LLM
    └── generation.py         # Generates answers using OpenAI with retrieved context
```

## Environment Variables

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
OPENAI_API_KEY=<your-openai-api-key>
```

## Key Commands

- **Start Neo4j:** `docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j`
- **Start Neo4j (if already created):** `docker start neo4j`
- **Ingest a document:** `python main.py ingest --file data/elon_musk.txt`
- **Ingest a folder:** `python main.py ingest --dir data/`
- **Ask a question:** `python main.py query "What companies did Elon Musk found?"`
- **Interactive Q&A:** `python main.py interactive`
- **Clear all data:** `python main.py reset`
- **Visualize graph (visual):** Open http://localhost:7474, login (`neo4j` / `password`), run `MATCH (n)-[r]->(m) RETURN n, r, m`
- **Visualize graph (table with relationship names):** `MATCH (n)-[r:RELATES_TO]->(m) RETURN n.name AS source, r.name AS relationship, r.fact AS fact, m.name AS target`

## Development Guidelines

- Use `async/await` throughout — Graphiti's API is fully asynchronous
- Always close the Graphiti client on shutdown using `try/finally` with `await client.close()`
- Use `.env` for all secrets — never hardcode API keys
- Pass timestamps when ingesting episodes for proper temporal reasoning
- Use `group_id` parameter for graph partitioning (default: `"default"`)
