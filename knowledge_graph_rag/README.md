# Knowledge Graph RAG

A question-answering system powered by AI. Feed in any document, and it builds a **knowledge graph** — a web of connected facts (people, companies, events, relationships) — then uses that graph to answer your questions accurately.

**Example:** You feed in a document about Elon Musk. It extracts facts like "Elon Musk founded SpaceX in 2002" and "SpaceX developed the Falcon 9 rocket". Then you ask "What is SpaceX?" and it gives you an accurate answer using those connected facts.

## How It Works

```
Your Document (e.g., elon_musk.txt)
     |
     v
[Ingestion] -- AI reads your text, picks out people, companies, events
     |
     v
[Knowledge Graph] -- Facts stored as connections in Neo4j database
     |                e.g., (Elon Musk) --[founded]--> (SpaceX)
     v
[You Ask a Question] -- "What companies did Elon Musk found?"
     |
     v
[Search] -- Finds relevant facts from the graph
     |
     v
[AI Answer] -- Gives you an accurate answer based on those facts
```

## Tech Stack

| Tool | What it does |
|------|-------------|
| **Python 3.11+** | Programming language |
| **Graphiti** (by Zep) | Extracts entities and relationships from text into a knowledge graph |
| **Neo4j** | Graph database that stores the knowledge graph (runs via Docker) |
| **OpenAI** (gpt-4o-mini) | AI that extracts facts during ingestion and generates answers |

---

## Getting Started

### Prerequisites

You need these 3 things installed before you begin:

1. **Python 3.11 or newer** — [Download here](https://www.python.org/downloads/)
   - Check if you have it: open a terminal and type `python --version`

2. **Docker Desktop** — [Download here](https://www.docker.com/products/docker-desktop/)
   - Make sure it's **open and running** before you proceed

3. **OpenAI API Key** — [Get one here](https://platform.openai.com/api-keys)
   - You need to add billing credits for it to work
   - Keep this key private, never share it

---

## Building the Project

You have two options to build this project:

### Option A: Build with Claude (Recommended)

1. Open [Claude](https://claude.ai) or Claude Code
2. Copy the entire contents of [`claude_build_prompt.md`](claude_build_prompt.md) and paste it to Claude
3. Claude will generate all the source code for you
4. Save the generated files into a `knowledge_graph_rag/` folder

### Option B: Clone this repo

If the project is already built and hosted:

```bash
git clone <repo-url>
cd knowledge_graph_rag
```

---

## Setting Up

### Step 1: Start the database

This downloads and starts Neo4j (the graph database) using Docker:

```bash
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j
```

Verify it's running: open http://localhost:7474 in your browser.
- Username: `neo4j`
- Password: `password`

> Already created the container before? Just run: `docker start neo4j`

### Step 2: Create a Python virtual environment

```bash
cd knowledge_graph_rag

# Create virtual environment
python -m venv venv

# Activate it (pick one for your terminal)
source venv/Scripts/activate    # Git Bash on Windows
venv\Scripts\activate           # Windows CMD / PowerShell
source venv/bin/activate        # Mac / Linux
```

### Step 3: Install packages

```bash
pip install -r requirements.txt
```

### Step 4: Add your OpenAI API key

```bash
cp .env.example .env
```

Open `.env` in any text editor and replace `your-openai-api-key-here` with your actual key:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
OPENAI_API_KEY=sk-proj-paste-your-key-here
```

---

## Running the Project

### 1. Ingest a document

Feed a document into the knowledge graph. A sample file about Elon Musk is included:

```bash
python main.py ingest --file data/elon_musk.txt
```

You can also ingest a whole folder of `.txt` or `.md` files:

```bash
python main.py ingest --dir data/
```

### 2. Ask questions

**Single question:**

```bash
python main.py query "What companies did Elon Musk found?"
```

**Interactive mode (ask multiple questions):**

```bash
python main.py interactive
```

Type your questions one at a time. Type `quit` to exit.

### 3. Visualize the knowledge graph

Open http://localhost:7474 in your browser, log in (`neo4j` / `password`), and run:

**Visual graph view (nodes and arrows):**

```
MATCH (n)-[r]->(m) RETURN n, r, m
```

**Table view with readable relationship names:**

```
MATCH (n)-[r:RELATES_TO]->(m)
RETURN n.name AS source, r.name AS relationship, r.fact AS fact, m.name AS target
```

> **Tip:** Graphiti stores all edges as `RELATES_TO` in Neo4j. The actual relationship meaning (e.g., "founded", "acquired") is in the edge properties `r.name` and `r.fact`. Use the table query above to see them, or click on any relationship arrow in the graph view to inspect its properties.

### 4. Reset the graph

Clear all data and start fresh:

```bash
python main.py reset
```

---

## Sample Questions to Try

```bash
python main.py query "What companies did Elon Musk found?"
python main.py query "Tell me about Elon Musk's early life"
python main.py query "What is SpaceX and what has it achieved?"
python main.py query "How did Elon Musk make his first fortune?"
python main.py query "What is Neuralink?"
python main.py query "Tell me about Tesla's history"
```

---

## Use Your Own Documents

1. Put your `.txt` or `.md` files in the `data/` folder
2. Run `python main.py ingest --dir data/`
3. Start asking questions!

The more detailed your documents, the better the answers.

---

## Project Files

```
knowledge_graph_rag/
├── main.py                  # Main program - you run this
├── README.md                # This file - project guide
├── claude_build_prompt.md   # Give this to Claude to build the project from scratch
├── CLAUDE.md                # Project config for Claude Code
├── requirements.txt         # List of packages to install
├── .env                     # Your secret keys (never share this)
├── .env.example             # Template for .env
├── data/
│   └── elon_musk.txt        # Sample document about Elon Musk
└── src/
    ├── __init__.py           # Makes src a Python package
    ├── config.py             # Loads settings from .env
    ├── graph_utils.py        # Connects to Neo4j via Graphiti
    ├── ingestion.py          # Reads documents and builds the graph
    ├── retrieval.py          # Searches the graph and formats context
    └── generation.py         # Generates answers using AI with context
```

---

## Troubleshooting

| Problem | What to do |
|---------|------------|
| `Connection refused` error | Make sure Docker Desktop is open and Neo4j is running. Try: `docker start neo4j` |
| `insufficient_quota` error | Add billing credits to your OpenAI account |
| `OPENAI_API_KEY` error | Check your `.env` file has a valid API key |
| No results from queries | Ingest data first: `python main.py ingest --file data/elon_musk.txt` |
| Want to start over | Run `python main.py reset` then ingest again |
| Docker command not found | Install Docker Desktop and make sure it's running |

---

## How It Works (For the Curious)

This project uses a technique called **Knowledge Graph RAG**:

- **RAG** (Retrieval-Augmented Generation) — the AI looks up relevant information before answering, instead of guessing from its training data.
- **Knowledge Graph** — instead of storing documents as plain text, we extract **entities** (people, companies, places) and **relationships** (founded, works at, acquired) and store them as a connected graph.

This is better than basic search because it understands **connections**. If you ask "Who works at the company Elon Musk founded in 2002?", it can follow the chain: Elon Musk -> founded -> SpaceX -> employees.

**Tools doing the work:**
- **Graphiti** (by Zep) — extracts entities and relationships from text
- **Neo4j** — stores the graph
- **OpenAI** (`gpt-4o-mini`) — extracts facts during ingestion, generates answers during queries
