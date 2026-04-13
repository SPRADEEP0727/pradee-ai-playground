# Graph RAG Project

## Overview
An advanced Graph RAG (Retrieval-Augmented Generation) system that builds on the foundational concepts from `KG_RAG/`. This project moves from educational/manual implementation to a more robust, framework-based approach for knowledge graph construction and querying.

## Goals
- Build a production-oriented Graph RAG pipeline
- Support multi-document ingestion and entity extraction
- Use a proper graph database (Neo4j) instead of in-memory NetworkX
- Implement advanced entity resolution and disambiguation
- Support multi-hop graph traversal for complex reasoning
- Provide a clean, modular Python codebase (not just notebooks)

## Tech Stack
- **LLM**: OpenAI GPT-4o-mini (via LangChain) for entity extraction and answer generation
- **Graph Database**: Neo4j (persistent, scalable graph storage)
- **Framework**: LangChain / LlamaIndex Graph or Graphiti for graph construction
- **Embeddings**: OpenAI embeddings for semantic entity matching
- **Environment**: Python 3.14+, dependencies managed via `requirements.txt`
- **Config**: API keys and DB credentials in `.env` (never commit this file)

## Architecture
```
documents/           → Source documents (text, PDF, etc.)
src/
  ingestion.py       → Document loading and chunking
  extraction.py      → LLM-based triplet extraction (subject, relation, object)
  graph_store.py     → Neo4j graph operations (add/query/update)
  entity_resolver.py → Entity matching and disambiguation
  retriever.py       → Graph traversal and context retrieval
  rag_pipeline.py    → End-to-end query pipeline
config.py            → Settings and environment loading
main.py              → CLI entry point
requirements.txt
.env                 → API keys (not committed)
```

## Key Improvements Over KG_RAG
| KG_RAG (Educational) | graph_rag (Production-Oriented) |
|---|---|
| In-memory NetworkX graph | Persistent Neo4j database |
| Single document | Multi-document ingestion |
| Basic string matching for entities | Embedding-based entity resolution |
| 1-hop neighbor retrieval | Multi-hop graph traversal |
| Single notebook | Modular Python package |
| No error handling | Proper error handling and logging |

## Development Guidelines
- Keep functions small and focused (single responsibility)
- Add type hints to all function signatures
- Use `python-dotenv` for all secrets — never hardcode API keys
- Write docstrings for public functions
- Prefer explicit over implicit — no magic globals
- Test extraction and retrieval independently before combining

## How to Run
```bash
# Install dependencies
pip install -r requirements.txt

# Set up .env with OPENAI_API_KEY and NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD

# Run the pipeline
python main.py --query "What companies does Elon Musk run?"
```
