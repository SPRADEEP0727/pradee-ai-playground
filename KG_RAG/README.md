# Knowledge Graph RAG (KG-RAG)

## What is Knowledge Graph RAG?

Instead of searching **chunks of text** (like basic RAG), Knowledge Graph RAG:
1. **Extracts entities and relationships** from text (e.g., "Elon Musk" → CEO of → "Tesla")
2. **Builds a graph** where nodes = entities, edges = relationships
3. **Queries the graph** to find connected information and answer questions

## How It Works — Step by Step

```
Text Document
     │
     ▼
LLM extracts triplets:  (Subject) --[Relation]--> (Object)
     │
     ▼
Build Graph:  Nodes = Entities,  Edges = Relationships
     │
     ▼
User asks a Question
     │
     ▼
Extract entities from question
     │
     ▼
Search graph for matching entities + neighbors
     │
     ▼
Collect related facts as context
     │
     ▼
LLM generates answer using graph facts
```

### Example with Elon Musk

**Input text:**
> Elon Musk is the CEO of Tesla. Tesla is an electric vehicle company. Elon Musk is the CEO of SpaceX. SpaceX developed the Falcon 9 rocket.

**Step 1 — Extract triplets:**
```
("Elon Musk", "is CEO of", "Tesla")
("Tesla", "is", "an electric vehicle company")
("Elon Musk", "is CEO of", "SpaceX")
("SpaceX", "developed", "Falcon 9")
```

**Step 2 — Build graph:**
```
Elon Musk --[is CEO of]--> Tesla
Elon Musk --[is CEO of]--> SpaceX
Tesla --[is]--> electric vehicle company
SpaceX --[developed]--> Falcon 9
```

**Step 3 — User asks:** *"What companies does Elon Musk run?"*

- Extracts entity: `["Elon Musk"]`
- Finds in graph: `Elon Musk`
- Collects facts: `Elon Musk is CEO of Tesla`, `Elon Musk is CEO of SpaceX`
- LLM answers: **"Elon Musk runs Tesla and SpaceX."**

## Project Structure

```
KG_RAG/
├── document.txt                 # Source text with Elon Musk facts
├── knowledge_graph_rag.ipynb    # Main notebook with full implementation
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Implementation Details

The notebook (`knowledge_graph_rag.ipynb`) contains these steps:

| Step | What it does | Key function / library |
|------|-------------|----------------------|
| 1 | Import libraries & setup LLM | `langchain_openai.ChatOpenAI` |
| 2 | Load `document.txt` | Python `open()` |
| 3 | Extract triplets from text using LLM | `extract_triplets()` — sends text to GPT-4o-mini, gets back JSON list of `[subject, relation, object]` |
| 4 | Build knowledge graph | `networkx.DiGraph()` — adds entities as nodes, relationships as edges |
| 5 | Visualize the graph | `matplotlib` — draws nodes (blue circles) and edges (arrows with labels) |
| 6 | Query the graph (RAG pipeline) | `knowledge_graph_rag()` — full pipeline function |

### Key Functions

#### `extract_triplets(text)`
- Sends the full text to GPT-4o-mini with a prompt asking for `[subject, relationship, object]` triplets
- Parses the JSON response and returns a list of triplets
- Handles markdown code block wrappers in LLM output

#### `get_entity_context(graph, entity)`
- Takes a graph and an entity name
- Returns all facts (both outgoing and incoming edges) for that entity
- Example: `get_entity_context(graph, "Elon Musk")` → `["Elon Musk is CEO of Tesla", "Elon Musk is CEO of SpaceX", ...]`

#### `find_matching_entities(graph, query_entities)`
- Matches entity names from the user's question to nodes in the graph
- Uses case-insensitive substring matching
- Example: user says "Tesla" → matches node "Tesla" in graph

#### `knowledge_graph_rag(query)` — The Main Pipeline
1. **Extract entities** from the user's question using LLM
2. **Match entities** to graph nodes
3. **Collect facts** from matched entities + their 1-hop neighbors (for richer context)
4. **Generate answer** by sending the collected facts + question to LLM

## Knowledge Graph RAG vs Basic RAG

| Feature | Basic RAG | Knowledge Graph RAG |
|---------|-----------|-------------------|
| Storage | Text chunks in vector DB | Entities + Relationships in graph |
| Search | Similarity/embedding search | Graph traversal |
| Best for | General Q&A | Relationship questions |
| Example | "Tell me about Elon Musk" | "What companies does Elon Musk run and what do they build?" |
| Multi-hop | Weak | Strong — follows connections across entities |

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment variables
Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

### 3. Run the notebook
Open `knowledge_graph_rag.ipynb` in Jupyter or VS Code and run all cells.

## Tech Stack

- **LangChain + OpenAI (GPT-4o-mini)** — for entity extraction and answer generation
- **NetworkX** — for building and querying the in-memory knowledge graph
- **Matplotlib** — for graph visualization
- **python-dotenv** — for loading API keys from `.env`
