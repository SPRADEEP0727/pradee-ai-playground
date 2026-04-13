# Knowledge Graph RAG - Quick Start Guide

## What is this?

This project lets you **ask questions about your documents** using AI. Instead of just searching for keywords, it builds a **knowledge graph** — a web of connected facts — from your documents, then uses that understanding to answer your questions accurately.

**Example:**
- You feed in a document about a company
- It extracts facts like "Alice founded Acme Corp" and "Acme Corp built MedGraph"
- You ask "Who founded Acme Corp?" and it answers using those connected facts

---

## Before You Begin

Make sure you have these installed on your machine before starting:

1. **Python 3.11 or higher** - [Download here](https://www.python.org/downloads/) if you don't have it. To check, run `python --version` in your terminal.
2. **Docker** - [Download here](https://www.docker.com/products/docker-desktop/). Make sure Docker Desktop is open and running before you proceed.
3. **OpenAI API key** - You need this for the AI to work. Sign up and get your key at https://platform.openai.com/api-keys. Keep this key private and never share it.

---

## Setup (One-Time)

### Step 1: Start the database

This project uses Neo4j (a graph database) to store the knowledge graph. Run it with Docker:

```bash
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j
```

You can verify it's running by visiting http://localhost:7474 in your browser.

### Step 2: Create a virtual environment

```bash
# Create it
python -m venv venv

# Activate it (pick one based on your terminal)
source venv/Scripts/activate    # Git Bash on Windows
venv\Scripts\activate           # Windows CMD
source venv/bin/activate        # Mac / Linux
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set up your API key

Copy the example env file and add your OpenAI key:

```bash
cp .env.example .env
```

Then edit `.env` and replace `your-openai-api-key-here` with your actual key:

```
OPENAI_API_KEY=sk-proj-your-key-here
```

---

## Usage

### 1. Ingest a document

Before you can ask questions, you need to feed in some data. A sample file is included:

```bash
python main.py ingest --file data/sample_company.txt
```

You can also ingest a whole folder of `.txt` or `.md` files:

```bash
python main.py ingest --dir data/
```

### 2. Ask a question

```bash
python main.py query "Who founded Acme Corp?"
```

This will:
1. Search the knowledge graph for relevant facts
2. Show you the retrieved context
3. Give you an AI-generated answer

### 3. Interactive mode

For asking multiple questions in a row:

```bash
python main.py interactive
```

Type your questions one by one. Type `quit` to exit.

### 4. Reset the graph

To clear all data and start fresh:

```bash
python main.py reset
```

---

## Using Your Own Documents

1. Place your `.txt` or `.md` files in the `data/` folder
2. Run `python main.py ingest --dir data/`
3. Start querying!

**Tip:** The more detailed your documents, the richer the knowledge graph and the better the answers.

---

## How It Works (Simple Explanation)

```
Your Documents
     |
     v
[Ingestion] -- AI reads your text and extracts entities & relationships
     |
     v
[Knowledge Graph] -- Facts stored as connected nodes in Neo4j
     |               e.g., (Alice) --[founded]--> (Acme Corp)
     v
[Your Question] -- "Who founded Acme Corp?"
     |
     v
[Search] -- Finds relevant facts from the graph
     |
     v
[AI Answer] -- Uses those facts to give you an accurate response
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` on port 7687 | Make sure Neo4j is running: `docker start neo4j` |
| `OPENAI_API_KEY` error | Check your `.env` file has a valid key |
| No results from queries | Run `python main.py ingest --file data/sample_company.txt` first |
| Want to start over | Run `python main.py reset` then re-ingest your documents |

---

## Project Structure

```
knowledge_graph_rag/
├── main.py              # Entry point - run this
├── .env                 # Your API keys (don't share this)
├── data/                # Put your documents here
│   └── sample_company.txt
├── src/
│   ├── config.py        # Loads settings from .env
│   ├── graph_utils.py   # Database connection helpers
│   ├── ingestion.py     # Turns documents into graph data
│   ├── retrieval.py     # Searches the knowledge graph
│   └── generation.py    # Generates answers using AI
└── venv/                # Virtual environment (don't edit)
```
