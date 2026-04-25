"""
Self-RAG = RAG + self-evaluation + retry.

Flow:
  1. user asks question
  2. retrieve documents
  3. generate answer
  4. LLM evaluates its own answer (supported by context? answers the question?)
  5. if bad -> rewrite the question, retrieve again, regenerate
  6. return the final answer
"""

import os
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load .env from the project folder (works no matter where streamlit is run from)
HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(find_dotenv(usecwd=False) or os.path.join(HERE, ".env"))
load_dotenv(os.path.join(os.path.dirname(HERE), ".env"))  # also check parent folder

# temperature=0 -> deterministic evaluator
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# Build FAISS vector store from knowledge.txt
def build_retriever(path: str = None, k: int = 3):
    if path is None:
        path = os.path.join(HERE, "knowledge.txt")
    docs = TextLoader(path, encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=300).split_documents(docs)
    vectorstore = FAISS.from_documents(chunks, OpenAIEmbeddings())
    return vectorstore.as_retriever(search_kwargs={"k": k})


# Forces the LLM to reply with {"answer": "yes"/"no"}
class YesNo(BaseModel):
    answer: str = Field(description="'yes' or 'no'")


# STEP 3: generate answer from retrieved context
def generate_answer(question: str, context: str) -> str:
    return llm.invoke(
        f"Answer the question using ONLY this context.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    ).content


# STEP 4: LLM evaluates its OWN answer
def evaluate_answer(question: str, answer: str, context: str) -> bool:
    result = llm.with_structured_output(YesNo).invoke(
        f"Is the answer good? It must be:\n"
        f"- supported by the context (no hallucination)\n"
        f"- actually answers the question\n\n"
        f"Question: {question}\nContext: {context}\nAnswer: {answer}\n"
        f"Reply only 'yes' or 'no'."
    )
    return result.answer.lower() == "yes"


# STEP 5 helper: rewrite the query so retrieval brings back different chunks
def rewrite_question(question: str) -> str:
    return llm.invoke(
        f"Rewrite this question to be clearer and more specific for "
        f"document search. Return only the rewritten question.\n\n"
        f"Question: {question}"
    ).content.strip()


# The Self-RAG pipeline — called by app.py
def self_rag(question: str, retriever, max_retries: int = 1) -> dict:
    print(f"\n--- new question: {question!r}")
    attempts = []
    current_q = question

    for i in range(max_retries + 1):
        print(f"\n[attempt {i + 1}]")

        # STEP 2: retrieve
        chunks = retriever.invoke(current_q)
        print(f"  retrieve   -> {len(chunks)} chunks for query {current_q!r}")
        context = "\n\n".join(c.page_content for c in chunks)

        # STEP 3: generate
        answer = generate_answer(question, context)
        print(f"  generate   -> {len(answer)} chars")

        # STEP 4: evaluate
        good = evaluate_answer(question, answer, context)
        print(f"  evaluate   -> {'GOOD' if good else 'BAD'}")

        attempts.append({
            "query": current_q,
            "chunks": chunks,
            "answer": answer,
            "good": good,
        })

        # STEP 5: good -> stop; bad -> rewrite & loop
        if good:
            break
        if i < max_retries:
            current_q = rewrite_question(question)
            print(f"  rewrite    -> {current_q!r}")

    print(f"--- done ({len(attempts)} attempt(s))\n")

    # STEP 6: final answer = last attempt
    final = attempts[-1]
    return {
        "attempts": attempts,
        "answer": final["answer"],
        "good": final["good"],
    }
