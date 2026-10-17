import os
import sys
from pathlib import Path

import requests
import streamlit as st

# Streamlit puts only THIS file's folder on the Python path, not the project
# root. This line adds the project root, so "from app...." imports always work.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.config.settings import ALLOWED_MODEL_NAMES  # noqa: E402

API_URL = os.getenv("API_URL", "http://127.0.0.1:9999/chat")

st.set_page_config(page_title="Multi AI Agent", page_icon="🤖", layout="wide")
st.title("Multi AI Agent")
st.caption("Choose a model, write a persona, and ask anything. Web search is optional.")

# ---------- Sidebar (settings) ----------
with st.sidebar:
    st.header("Configuration")
    selected_model = st.selectbox("Select Model", ALLOWED_MODEL_NAMES)
    allow_web_search = st.toggle("Allow Web Search", value=False)
    send_context = st.toggle("Send conversation context", value=False)
    system_prompt = st.text_area(
        "Define Your AI Agent",
        placeholder="You are a helpful AI assistant...",
        height=150,
    )
    if st.button("Clear chat"):
        st.session_state.history = []
        st.rerun()

# ---------- Chat history ----------
if "history" not in st.session_state:
    st.session_state.history = []

for item in st.session_state.history:
    with st.chat_message(item["role"]):
        st.write(item["content"])

# ---------- New question ----------
user_query = st.chat_input("Enter your query...")

if user_query:
    st.session_state.history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    if send_context:
        messages = [h["content"] for h in st.session_state.history if h["role"] == "user"]
    else:
        messages = [user_query]

    payload = {
        "model_name": selected_model,
        "system_prompt": system_prompt or "You are a helpful AI assistant.",
        "messages": messages,
        "allow_search": allow_web_search,
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = requests.post(API_URL, json=payload, timeout=120)
                if reply.status_code == 200:
                    answer = reply.json().get("response", "No response")
                    st.write(answer)
                    st.session_state.history.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Failed to get response from AI Agent (status code {reply.status_code})")
                    with st.expander("Error details"):
                        st.code(reply.text)
            except requests.exceptions.RequestException as e:
                st.error("Could not reach the backend. Is it running on port 9999?")
                with st.expander("Error details"):
                    st.code(str(e))