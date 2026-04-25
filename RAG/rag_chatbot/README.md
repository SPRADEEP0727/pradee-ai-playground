# Self-RAG Chatbot — Student Demo

A simple chatbot that demonstrates **Self-RAG** (Self-Retrieval-Augmented Generation) with a Streamlit UI.

## What is Self-RAG?

**Self-RAG = RAG + self-evaluation + retry.**

The LLM does the normal RAG flow, then **evaluates its own answer**. If the answer is not good enough, it rewrites the question, retrieves new documents, and generates again.

> Like a student who writes an answer, re-reads it, and says *"wait, that's not backed by my notes"* — then fixes it.

### The 6 steps

1. User asks a question
2. Retrieve documents from the vector store
3. Generate an answer
4. LLM evaluates its own answer (supported by context? answers the question?)
5. If bad → rewrite the question, retrieve again, regenerate
6. Return the final answer

## Project structure

```
rag_chatbot/
├── app.py            # Streamlit UI
├── self_rag.py       # Self-RAG core logic (no UI)
├── knowledge.txt     # The documents the bot can answer from
├── requirements.txt  # Python dependencies
└── README.md
```

Logic and UI are kept in separate files so students can read `self_rag.py` as a pure recipe, without Streamlit getting in the way.

## How to run it

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

Create a `.env` file in this folder (or in any parent folder):

```
OPENAI_API_KEY=sk-...your-key-here...
```

### 3. Launch the app

```bash
streamlit run app.py
```

The chatbot opens at **http://localhost:8501**.

## Try asking

- `What is hybrid RAG?`
- `Why do we need RAG?`
- `List the core components of RAG`
- `What is the capital of France?` *(off-topic — watch the evaluator reject it)*

For each answer, open the **"See the Self-RAG attempts"** panel to see:
- The query used
- How many chunks were retrieved
- The answer produced
- The evaluator's verdict (`GOOD — stop` or `BAD — retry`)

## How it maps to the code

| Step | Function in `self_rag.py` |
|------|---------------------------|
| 2. Retrieve | `retriever.invoke(query)` |
| 3. Generate | `generate_answer()` |
| 4. Evaluate | `evaluate_answer()` |
| 5. Rewrite & retry | `rewrite_question()` + loop in `self_rag()` |
| 6. Return | last item of `attempts` |
