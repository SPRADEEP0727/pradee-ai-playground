# Prompt: Build a Knowledge Graph RAG System

Copy everything below and give it to Claude to build this project from scratch.

---

## What to Build

Build a Knowledge Graph RAG (Retrieval-Augmented Generation) system in Python. This system:
1. Reads text documents and extracts entities (people, companies, places) and relationships
2. Stores them as a knowledge graph in Neo4j
3. Lets users ask questions and get AI-generated answers based on the graph

### Tech Stack

- **Python 3.11+**
- **Graphiti** (`graphiti-core`) by Zep - extracts entities and relationships from text into a knowledge graph
- **Neo4j** - graph database that stores the knowledge graph (run via Docker)
- **OpenAI** (`gpt-4o-mini`) - LLM for entity extraction during ingestion and answer generation during queries
- **python-dotenv** - loads environment variables from `.env`
- **pydantic** - data validation

### Project Structure

Create these files:

```
knowledge_graph_rag/
├── main.py                  # CLI entry point - run this file
├── README.md                # Beginner-friendly setup and usage guide
├── requirements.txt         # Python dependencies
├── .env.example             # Template for environment variables
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

### What Each File Should Do

#### `requirements.txt`
```
graphiti-core
neo4j
openai
python-dotenv
pydantic
```

#### `.env.example`
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
OPENAI_API_KEY=your-openai-api-key-here
```

#### `src/config.py`
- Load `.env` using `python-dotenv`
- Export: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `OPENAI_API_KEY`
- Use sensible defaults for Neo4j settings

#### `src/graph_utils.py`
- `get_graphiti_client()` - Create a `Graphiti` client with Neo4j credentials, call `build_indices_and_constraints()`, return it
- `close_client(client)` - Call `client.close()`
- `clear_graph(client)` - Run Cypher `MATCH (n) DETACH DELETE n` to wipe the graph

#### `src/ingestion.py`
- `ingest_text(client, text, name, ...)` - Ingest a text block as an episode using `client.add_episode()` with `EpisodeType.text`
- `ingest_file(client, file_path, ...)` - Read a file and call `ingest_text()`
- `ingest_directory(client, dir_path, ...)` - Ingest all `.txt`/`.md` files from a directory
- Print how many nodes and edges were extracted

#### `src/retrieval.py`
- `search_graph(client, query, ...)` - Call `client.search()` to find relevant edges
- `format_context(edges)` - Turn the edges into a numbered list of facts
- `retrieve_context(client, query, ...)` - Search + format in one call

#### `src/generation.py`
- Use `AsyncOpenAI` client
- System prompt: tell the LLM to answer ONLY from the provided context
- `generate_response(query, context, model="gpt-4o-mini")` - Call OpenAI chat completions, temperature 0.3

#### `main.py`
CLI with 4 subcommands using argparse:
- `ingest` - with `--file`, `--dir`, `--group` options
- `query` - takes a question as argument, prints retrieved context and AI answer
- `interactive` - loop that keeps asking for questions until user types "quit"
- `reset` - clears all data from the graph

All commands are async (use `asyncio.run()`). Always close the Graphiti client in a `try/finally` block.

#### `data/elon_musk.txt`
Create a detailed document about Elon Musk covering:
- Early life (born 1971, Pretoria, South Africa; parents Maye and Errol Musk; siblings Kimbal and Tosca)
- Childhood (self-taught programming, created Blastar game at age 12)
- Education (Queen's University Canada, University of Pennsylvania - Economics & Physics, dropped out of Stanford PhD)
- Zip2 (1995, co-founded with Kimbal, sold to Compaq for $307M)
- X.com / PayPal (1999, merged with Confinity, sold to eBay for $1.5B)
- SpaceX (2002, Falcon rockets, Dragon spacecraft, Crew Dragon, Starship)
- Tesla (joined 2004, CEO from 2008, Roadster, Model S/X/3/Y, Gigafactories)
- SolarCity / Tesla Energy (2006, acquired by Tesla 2016, Powerwall/Megapack)
- Neuralink (2016, brain-computer interfaces)
- The Boring Company (2016, tunnel construction, Vegas Loop)
- xAI (2023, Grok AI chatbot)
- Twitter/X acquisition (2022, $44B, rebranded to X in 2023)
- Awards (Time Person of the Year 2021, richest person)

### Important Implementation Notes

1. **Everything is async** - Graphiti's API uses `async/await` throughout
2. **Always close the client** - Use `try/finally` to ensure `client.close()` is called
3. **Never hardcode API keys** - Load from `.env` file
4. **Pass timestamps** when ingesting for proper temporal reasoning
5. **Group IDs** allow partitioning the graph (default: `"default"`)

### How to Test After Building

1. Start Neo4j:
   ```bash
   docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j
   ```

2. Set up environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate   # or venv\Scripts\activate on Windows CMD
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. Ingest sample data:
   ```bash
   python main.py ingest --file data/elon_musk.txt
   ```

4. Run queries:
   ```bash
   python main.py query "What companies did Elon Musk found?"
   python main.py query "What is SpaceX and what has it achieved?"
   python main.py query "Tell me about Elon Musk's early life"
   python main.py interactive
   ```

5. Visualize the graph at http://localhost:7474 (login: `neo4j` / `password`) with:
   ```cypher
   MATCH (n)-[r]->(m) RETURN n, r, m
   ```
