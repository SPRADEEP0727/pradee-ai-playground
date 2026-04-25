"""
Streamlit UI for the RAG chatbot.
Logic lives in self_rag.py. Run:  streamlit run app.py
"""

import os
import streamlit as st
from self_rag import build_retriever, self_rag

st.set_page_config(page_title="RAG Chatbot", layout="centered")
st.title("RAG Chatbot")
st.caption("Ask me anything about RAG.")

# Fail fast with a visible message if the API key isn't loaded
if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found. Put it in a `.env` file in this folder or its parent.")
    st.stop()

with st.sidebar:
    st.header("Try asking")
    st.markdown(
        "- What is hybrid RAG?\n"
        "- Why do we need RAG?\n"
        "- List the core components of RAG\n"
        "- What are the limitations of RAG?"
    )
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


# Cached so we build the vector store only once
@st.cache_resource
def get_retriever():
    return build_retriever()


try:
    retriever = get_retriever()
except Exception as e:
    st.error(f"Failed to build retriever: {e}")
    st.stop()

# Chat history survives Streamlit reruns via session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])


if question := st.chat_input("Ask about RAG..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = self_rag(question, retriever)
        st.markdown(result["answer"])

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
