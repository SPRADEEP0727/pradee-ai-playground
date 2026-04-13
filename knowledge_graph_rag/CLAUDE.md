# Knowledge Graph RAG

## Project Overview

A Retrieval-Augmented Generation (RAG) system built on knowledge graphs using the **Graphiti** framework by Zep. Graphiti builds dynamic, temporally-aware knowledge graphs from unstructured data, enabling more contextual and accurate retrieval than traditional vector-based RAG.

## Tech Stack

- **Language:** Python 3.11+
- **Knowledge Graph Framework:** [Graphiti](https://github.com/getzep/graphiti) (by Zep)
- **Graph Database:** Neo4j (required by Graphiti)
- **LLM Provider:** OpenAI (default Graphiti integration)
- **Embedding Model:** OpenAI text-embedding-3-small (default)

## Architecture

```
User Query → Graphiti Search → Knowledge Graph (Neo4j) → Context Assembly → LLM → Response
                                      ↑
                          Document Ingestion Pipeline
                          (episodes → nodes + edges)
```

### Core Concepts (Graphiti)

- **Episodes:** Units of ingested data (text, messages, documents). Each episode is processed into graph nodes and edges.
- **Entity Nodes:** Extracted entities stored as graph nodes with embeddings.
- **Edges (Relations):** Typed relationships between entities, also with embeddings.
- **Temporal Awareness:** All nodes and edges carry timestamps, enabling point-in-time queries and handling of evolving facts.
- **Community Detection:** Graphiti groups related entities into communities for broader context retrieval.

## Project Structure

```
knowledge_graph_rag/
├── CLAUDE.md
├── requirements.txt
├── .env                  # API keys and Neo4j connection (not committed)
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuration and environment loading
│   ├── ingestion.py      # Document ingestion into Graphiti
│   ├── retrieval.py      # Knowledge graph search and context retrieval
│   ├── generation.py     # LLM response generation with retrieved context
│   └── graph_utils.py    # Neo4j and Graphiti helper utilities
├── data/                 # Source documents for ingestion
├── notebooks/            # Experimentation notebooks
└── tests/
```

## Environment Variables

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<password>
OPENAI_API_KEY=<key>
```

## Setup

1. Start Neo4j (Docker recommended): `docker run -p 7474:7474 -p 7687:7687 neo4j`
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in credentials
4. Run ingestion, then query

## Key Commands

- **Install deps:** `pip install graphiti-core neo4j openai python-dotenv`
- **Run Neo4j:** `docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j`
- **Neo4j Browser:** http://localhost:7474

## Development Guidelines

- Use `async/await` throughout — Graphiti's API is fully asynchronous
- Always close the Graphiti client on shutdown (`await graphiti.close()`)
- Use `.env` for all secrets; never hardcode API keys
- Add temporal metadata (timestamps) when ingesting episodes for proper temporal reasoning
- Prefer `graphiti.search()` with hybrid search (combining BM25 + embedding similarity) for retrieval
