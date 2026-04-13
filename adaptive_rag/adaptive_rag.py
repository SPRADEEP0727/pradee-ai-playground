"""
Adaptive RAG with Fallback Mechanism
=====================================
Routes queries to the best retrieval strategy (Normal RAG or Web Search RAG)
and falls back to the alternate strategy if the primary one returns low-quality results.

Flow:
    User Query → Router → Normal RAG or Web Search RAG
                              ↓
                       Relevance Check
                         /         \
                       PASS        FAIL → Fallback to alternate strategy
                        ↓                        ↓
                  Generate Answer          Generate Answer
                                    (or LLM-only if both fail)

What is Adaptive RAG?
---------------------
Traditional RAG always searches a local vector store. But what if the answer
isn't in your documents? (e.g., "CSK score today" or "latest Python version")

Adaptive RAG solves this by:
1. ROUTING   — An LLM decides: search local docs OR search the web?
2. RETRIEVING — Fetches context from the chosen source
3. GRADING   — Checks if the retrieved context is good enough
4. FALLING BACK — If not good enough, tries the OTHER source
5. GENERATING — Produces the final answer from the best context found
"""

# ─────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────
import os
import sys

# LangChain: LLM and Embeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# LangChain: Vector Store for local document search
from langchain_community.vectorstores import FAISS

# LangChain: Load text files and split them into chunks
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

# Relevance threshold: if the similarity score is below this,
# we consider the retrieval result "not good enough" and trigger fallback.
# Range: 0.0 (irrelevant) to 1.0 (perfect match)
# Higher = stricter (fewer false positives but may miss valid results)
# Lower  = lenient (more results pass but may include irrelevant ones)
RELEVANCE_THRESHOLD = 0.75

# Paths — use absolute paths based on this file's location
# so the code works regardless of where you run it from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "faiss_index")   # Where FAISS index is saved
DOCUMENT_PATH = os.path.join(BASE_DIR, "documents", "document.txt")  # Local knowledge base

# These are initialized later (after .env is loaded) via init()
llm = None         # The language model (GPT-4o-mini)
embeddings = None  # The embedding model (for converting text → vectors)


def init():
    """
    Initialize LLM and Embeddings.

    WHY separate init()?
    → We need load_dotenv() to run FIRST (in main.py) so that
      OPENAI_API_KEY is available. If we created these at import time,
      the API key wouldn't be loaded yet and it would crash.
    """
    global llm, embeddings
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # temperature=0 for consistent answers
    embeddings = OpenAIEmbeddings()  # Uses OpenAI's text-embedding model


# =============================================================
# STEP 1: BUILD VECTOR STORE FROM LOCAL DOCUMENTS
# =============================================================
# This is the "Normal RAG" preparation step.
# We load a text file → split it into small chunks → convert each
# chunk into a vector (embedding) → store in FAISS for fast search.
#
# Think of it like creating a searchable index of your documents,
# similar to how Google indexes web pages.
# =============================================================

def build_vector_store():
    """
    Load documents, split into chunks, embed, and save to FAISS.

    Process:
        document.txt → TextLoader → ["chunk1", "chunk2", ...] → Embeddings → FAISS index
    """
    # Check if the document file exists
    if not os.path.exists(DOCUMENT_PATH):
        print(f"[ERROR] Document not found at '{DOCUMENT_PATH}'")
        print("Please add your documents to the 'documents/' folder.")
        sys.exit(1)

    print("[INFO] Loading and indexing documents...")

    # Load the text file into memory
    loader = TextLoader(DOCUMENT_PATH, encoding="utf-8")
    documents = loader.load()

    # Split into small overlapping chunks
    # chunk_size=300 → each chunk is ~300 characters
    # chunk_overlap=50 → 50 chars overlap between chunks (prevents cutting sentences)
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    # Convert chunks into vectors and store in FAISS
    # FAISS = Facebook AI Similarity Search (fast vector similarity search)
    vectorstore = FAISS.from_documents(chunks, embedding=embeddings)

    # Save to disk so we don't have to rebuild every time
    vectorstore.save_local(VECTOR_STORE_PATH)
    print(f"[INFO] Vector store created with {len(chunks)} chunks.")
    return vectorstore


def load_vector_store():
    """
    Load existing FAISS index from disk, or build a new one if not found.
    This avoids re-embedding documents on every run (saves time and API calls).
    """
    if os.path.exists(VECTOR_STORE_PATH):
        return FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    return build_vector_store()


# =============================================================
# STEP 2: QUERY ROUTER
# =============================================================
# The Router is the "brain" of Adaptive RAG.
# It looks at the user's question and decides:
#   → "normal_rag"  = search local documents (e.g., "What is RAG?")
#   → "web_search"  = search the internet (e.g., "CSK score today")
#
# HOW? We ask the LLM itself to classify the query.
# =============================================================

def route_query(query: str) -> str:
    """
    Use the LLM to classify a query into one of two retrieval strategies.

    Example decisions:
        "What is RAG?"              → normal_rag  (topic is in our docs)
        "Who won the T20 WC?"       → web_search  (needs live/recent data)
        "Explain vector databases"  → normal_rag  (AI topic in our docs)
        "Weather in Mumbai"         → web_search  (real-time data needed)
    """
    # Ask the LLM to decide the best route
    response = llm.invoke(f"""
You are a query router. Given a user question, decide the best retrieval strategy.

Rules:
- If the question is about general knowledge, recent events, news, live data,
  or anything unlikely to be in a local knowledge base → return "web_search"
- If the question is about specific topics covered in documents (like RAG, AI concepts,
  company-specific data) → return "normal_rag"

Return ONLY one of: normal_rag, web_search

Question: {query}
""").content.strip().lower()

    # Parse the LLM's response — default to web_search if unclear
    route = "normal_rag" if "normal_rag" in response else "web_search"
    print(f"\n[ROUTER] Query: '{query}'")
    print(f"[ROUTER] Decision: {route}")
    return route


# =============================================================
# STEP 3: NORMAL RAG (Local Vector Store Search)
# =============================================================
# Searches your local FAISS vector store for relevant document chunks.
# Returns the chunks + a relevance score.
#
# HOW SIMILARITY SEARCH WORKS:
#   1. User query → converted to a vector (embedding)
#   2. FAISS finds the 4 closest vectors in the index
#   3. Returns documents + L2 distance scores
#   4. We convert L2 distance to a 0-1 relevance score
# =============================================================

def normal_rag(query: str, vectorstore) -> dict:
    """
    Retrieve relevant chunks from the local FAISS vector store.

    Returns a dict with:
        - context:  the retrieved text chunks joined together
        - relevant: True/False based on whether score >= threshold
        - source:   "normal_rag"
        - score:    0.0 to 1.0 relevance score
    """
    print("\n[NORMAL RAG] Searching local documents...")

    # Search FAISS for the 4 most similar chunks (k=4)
    # Returns: [(Document, score), (Document, score), ...]
    docs_with_scores = vectorstore.similarity_search_with_score(query, k=4)

    # No results found
    if not docs_with_scores:
        return {"context": "", "relevant": False, "source": "normal_rag"}

    # FAISS returns L2 (Euclidean) distance — LOWER is BETTER
    # L2 = 0 means identical, L2 ≈ 2 means very different
    # Convert to relevance: relevance = 1 - (distance / 2)
    # So: distance=0 → relevance=1.0, distance=2 → relevance=0.0
    best_score = docs_with_scores[0][1]  # Best (lowest) distance
    relevance = max(0, 1 - (best_score / 2))

    # Combine all retrieved chunks into one context string
    context = "\n".join([doc.page_content for doc, score in docs_with_scores])

    print(f"[NORMAL RAG] Retrieved {len(docs_with_scores)} chunks")
    print(f"[NORMAL RAG] Best relevance score: {relevance:.2f} (threshold: {RELEVANCE_THRESHOLD})")

    return {
        "context": context,
        "relevant": relevance >= RELEVANCE_THRESHOLD,  # Pass/Fail check
        "source": "normal_rag",
        "score": relevance,
    }


# =============================================================
# STEP 4: WEB SEARCH RAG (SerpAPI — Google Search)
# =============================================================
# When the query needs live/recent data that's not in local docs,
# we search the web using SerpAPI (a Google Search API).
#
# SerpAPI returns a rich JSON response with multiple sections:
#   - answer_box:      Direct answer (e.g., "Paris" for "capital of France")
#   - knowledge_graph:  Wikipedia-style summary
#   - organic_results:  Regular Google search results with snippets
#   - sports_results:   Live scores, match data
#
# We extract ALL useful sections to give the LLM maximum context.
# =============================================================

def _serialize_serp_results(results: dict) -> str:
    """
    Convert the full SerpAPI JSON response into clean, readable text.

    SerpAPI returns a complex nested dict. We extract only the useful parts
    and format them as plain text so the LLM can easily read and reason over them.

    Sections extracted (in priority order):
        1. Answer Box   → Google's direct answer (most concise)
        2. Knowledge Graph → Wikipedia-style info
        3. Organic Results → Regular search snippets (most reliable)
        4. Sports Results  → Live scores and match data
    """
    parts = []

    # 1. Answer box — Google's direct answer (e.g., "The capital of France is Paris")
    if "answer_box" in results:
        ab = results["answer_box"]
        if isinstance(ab, dict):
            parts.append(f"Direct Answer: {ab.get('answer', ab.get('snippet', ''))}")
        else:
            parts.append(f"Direct Answer: {ab}")

    # 2. Knowledge graph — Wikipedia-style summary from Google
    if "knowledge_graph" in results:
        kg = results["knowledge_graph"]
        if isinstance(kg, dict):
            desc = kg.get("description", "")
            title = kg.get("title", "")
            if title or desc:
                parts.append(f"Knowledge Graph: {title} — {desc}")

    # 3. Organic search results — regular Google results with title + snippet
    #    These are the most reliable for factual questions
    if "organic_results" in results:
        for r in results["organic_results"][:5]:  # Top 5 results
            snippet = r.get("snippet", "")
            title = r.get("title", "")
            if snippet:
                parts.append(f"- {title}: {snippet}")

    # 4. Sports results — live scores, match data (for cricket, football, etc.)
    if "sports_results" in results:
        sr = results["sports_results"]
        if "title" in sr:
            parts.append(f"\nSports: {sr['title']}")
        for game in sr.get("games", [])[:3]:  # Show top 3 matches
            teams = " vs ".join([f"{t['name']} ({t.get('score', '')})" for t in game.get("teams", [])])
            parts.append(f"  {game.get('date', '')} | {teams} | {game.get('status', '')}")

    # If none of the known sections were found, dump raw JSON as fallback
    if not parts:
        import json
        return json.dumps(results, indent=2, ensure_ascii=False)[:3000]

    return "\n".join(parts)


def web_search_rag(query: str) -> dict:
    """
    Search the web using SerpAPI (Google Search API) and return results.

    Uses the serpapi library directly (not LangChain's wrapper) because
    the full API gives us access to answer_box, knowledge_graph,
    organic_results, and sports_results — LangChain's wrapper only
    returns sports_results which is often not enough.

    Returns a dict with:
        - context:  formatted search results as readable text
        - relevant: True if we got meaningful content, False otherwise
        - source:   "web_search"
    """
    print("\n[WEB SEARCH RAG] Searching the web...")

    try:
        # Import SerpAPI's GoogleSearch (from google-search-results package)
        from serpapi import GoogleSearch

        # Set up search parameters
        params = {
            "q": query,                                        # The search query
            "api_key": os.environ.get("SERPAPI_API_KEY", ""),  # API key from .env
        }

        # Execute the search and get full response as a dict
        search = GoogleSearch(params)
        results = search.get_dict()

        # No results returned
        if not results:
            return {"context": "", "relevant": False, "source": "web_search"}

        # Convert the complex JSON into readable text
        context = _serialize_serp_results(results)
        print(f"[WEB SEARCH RAG] Got search results")

        # Simple relevance check: if we got meaningful text (>20 chars), it's relevant.
        # The answer generator will handle cases where the data doesn't fully answer.
        # We don't use LLM-based grading here because it's unreliable with structured data.
        relevant = len(context.strip()) > 20
        print(f"[WEB SEARCH RAG] Has content: {relevant}")

        return {
            "context": context,
            "relevant": relevant,
            "source": "web_search",
        }

    except Exception as e:
        print(f"[WEB SEARCH RAG] Error: {e}")
        return {"context": "", "relevant": False, "source": "web_search"}


# =============================================================
# STEP 5: GENERATE FINAL ANSWER
# =============================================================
# Once we have retrieved context (from local docs or web search),
# we pass it to the LLM along with the user's question.
# The LLM generates a concise answer based on the context.
# =============================================================

def generate_answer(query: str, context: str, source: str) -> str:
    """
    Generate the final answer using the LLM + retrieved context.

    The prompt tells the LLM to:
    - Use ONLY the provided context to answer
    - Handle structured data (JSON, scores, tables) by reasoning over it
    - Honestly say if the context doesn't contain the answer
    """
    response = llm.invoke(f"""
Answer the user's question using the provided context. Be accurate and concise.
The context may contain structured data (scores, tables, JSON, match results) —
analyze and reason over it to derive the answer, even if the answer isn't stated directly.
If the context truly doesn't contain relevant information, say so honestly.

Context:
{context}

Question: {query}
Answer:
""").content.strip()
    return response


def generate_fallback_answer(query: str) -> str:
    """
    Last resort fallback: when BOTH normal RAG and web search fail,
    the LLM answers from its own training knowledge with a disclaimer.

    This ensures the user always gets SOME answer, even if it may not
    be up-to-date (since the LLM's knowledge has a cutoff date).
    """
    print("\n[FALLBACK] Both retrieval strategies failed. Using LLM knowledge only.")
    response = llm.invoke(f"""
Answer this question from your own knowledge. Be concise and accurate.
Start your answer with: "Note: This answer is generated from general knowledge
as no relevant documents or web results were found."

Question: {query}
""").content.strip()
    return response


# =============================================================
# STEP 6: ADAPTIVE RAG — MAIN ORCHESTRATOR
# =============================================================
# This is the main function that ties everything together.
# It implements the full adaptive flow with fallback:
#
#   1. ROUTE   → Decide: normal_rag or web_search?
#   2. TRY     → Execute the chosen strategy
#   3. CHECK   → Is the result relevant enough?
#   4. FALLBACK → If not, try the OTHER strategy
#   5. LAST RESORT → If both fail, use LLM's own knowledge
#
# Example flows:
#   "What is RAG?"    → Router: normal_rag → FAISS search → score 0.86 ✓ → Answer
#   "CSK score today" → Router: web_search → SerpAPI → has content ✓ → Answer
#   "obscure question"→ Router: web_search → SerpAPI fails → Fallback: normal_rag
#                      → FAISS score 0.50 ✗ → LLM-only answer with disclaimer
# =============================================================

def adaptive_rag(query: str) -> str:
    """
    Main orchestrator: routes the query, retrieves context, checks relevance,
    and falls back to an alternate strategy if needed.

    Args:
        query: The user's question

    Returns:
        The generated answer string
    """
    print("=" * 60)
    print(f"  ADAPTIVE RAG — Processing Query")
    print("=" * 60)

    # Load the FAISS vector store (builds it on first run)
    vectorstore = load_vector_store()

    # ── Step 1: Route the query ──
    # LLM decides: should we search local docs or the web?
    route = route_query(query)

    # ── Step 2: Try the PRIMARY retrieval strategy ──
    if route == "normal_rag":
        primary = normal_rag(query, vectorstore)  # Search local FAISS
    else:
        primary = web_search_rag(query)            # Search Google via SerpAPI

    # ── Step 3: If primary returned relevant results → generate answer ──
    if primary["relevant"]:
        print(f"\n[RESULT] Primary strategy ({primary['source']}) returned relevant results.")
        answer = generate_answer(query, primary["context"], primary["source"])
        print_answer(answer, primary["source"])
        return answer

    # ── Step 4: Primary FAILED → try the FALLBACK (opposite) strategy ──
    # If normal_rag failed → try web_search, and vice versa
    print(f"\n[FALLBACK] Primary strategy ({primary['source']}) returned low-relevance results.")
    print("[FALLBACK] Trying alternate strategy...")

    if route == "normal_rag":
        fallback = web_search_rag(query)           # Normal RAG failed → try web
    else:
        fallback = normal_rag(query, vectorstore)  # Web failed → try local docs

    # ── Step 5: If fallback returned relevant results → generate answer ──
    if fallback["relevant"]:
        print(f"\n[RESULT] Fallback strategy ({fallback['source']}) returned relevant results.")
        answer = generate_answer(query, fallback["context"], fallback["source"])
        print_answer(answer, fallback["source"], is_fallback=True)
        return answer

    # ── Step 6: BOTH failed → LLM answers from its own knowledge ──
    # This is the last resort — always gives an answer but with a disclaimer
    answer = generate_fallback_answer(query)
    print_answer(answer, "llm_knowledge", is_fallback=True)
    return answer


def print_answer(answer: str, source: str, is_fallback: bool = False):
    """Pretty-print the final answer with its source."""
    print("\n" + "=" * 60)
    fallback_tag = " (via fallback)" if is_fallback else ""
    print(f"  SOURCE: {source}{fallback_tag}")
    print("=" * 60)
    print(f"\n{answer}\n")
