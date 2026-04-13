# Adaptive RAG

Adaptive Retrieval-Augmented Generation (RAG) is an advanced RAG pattern that intelligently routes queries to the most appropriate retrieval strategy based on the nature of the question.

## How It Works

Adaptive RAG uses a **router** to analyze the incoming query and decide the best retrieval path, with a built-in **fallback mechanism** to ensure reliable answers:

1. **Normal RAG** - For questions that can be answered from local documents/knowledge base
2. **Web Search RAG** - For questions requiring up-to-date or external information not available in local documents
3. **Fallback Mechanism** - If the primary retrieval path returns low-relevance results or fails, the system automatically falls back to the alternate strategy

```
User Query
    │
    ▼
┌─────────┐
│  Router  │ ── Analyzes query to determine best retrieval strategy
└─────────┘
    │
    ├──► Normal RAG (local vector store retrieval)
    │       │
    │       ▼
    │    Retrieve from FAISS/ChromaDB
    │       │
    │       ▼
    │   ┌────────────────┐
    │   │ Relevance Check │ ── Are retrieved docs relevant? (score > threshold)
    │   └────────────────┘
    │       │           │
    │      YES          NO (fallback)
    │       │           │
    │       ▼           ▼
    │   Generate    Web Search RAG ──► Generate Answer
    │   Answer
    │
    └──► Web Search RAG (external search)
            │
            ▼
         Search Web (SerpAPI)
            │
            ▼
        ┌────────────────┐
        │ Relevance Check │ ── Are search results useful?
        └────────────────┘
            │           │
           YES          NO (fallback)
            │           │
            ▼           ▼
        Generate    Normal RAG ──► Generate Answer
        Answer
```

### Fallback Strategy

| Primary Path | Trigger for Fallback | Fallback Action |
|---|---|---|
| Normal RAG | Retrieval score below threshold / empty results | Route to Web Search RAG |
| Web Search RAG | No relevant search results / API failure | Route to Normal RAG |
| Both fail | Neither path returns relevant results | LLM generates answer from its own knowledge with a disclaimer |

## Project Structure

```
adaptive_rag/
├── README.md
├── requirements.txt
├── .env.example            # Template for API keys
├── main.py                 # Entry point — run this to test
├── adaptive_rag.py         # Core logic (router, retrieval, fallback)
├── documents/
│   └── document.txt        # Local documents for normal RAG
└── faiss_index/            # Auto-generated FAISS vector store
```

> **Note:** Uses the shared `uv` virtual environment at `D:/genai/.venv` — no separate venv needed.

## Setup

1. Activate the shared uv environment (from `D:/genai`):
   ```bash
   # Windows
   D:\genai\.venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Create a .env file with your API keys
   OPENAI_API_KEY=your_openai_key
   SERPAPI_API_KEY=your_serpapi_key
   ```

## Key Components

- **Query Router**: Uses an LLM to classify whether a query needs local document retrieval or web search
- **Vector Store RAG**: Embeds local documents and retrieves relevant chunks using similarity search
- **Web Search RAG**: Uses SerpAPI to search the web and generate answers from search results
- **Relevance Grader**: Evaluates whether retrieved documents/results are relevant enough to answer the query (uses similarity score threshold or LLM-based grading)
- **Fallback Controller**: Automatically reroutes to the alternate retrieval strategy when the primary path fails or returns low-quality results
- **Response Generator**: Combines retrieved context with the query to produce a final answer

## Dependencies

- LangChain
- OpenAI / ChatOpenAI
- FAISS (vector store)
- SerpAPI (web search)
- python-dotenv
