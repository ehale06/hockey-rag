import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.rag_chain import ask

st.set_page_config(
    page_title="Hockey RAG Assistant",
    page_icon="🏒",
    layout="centered"
)

st.title("🏒 Hockey RAG Assistant")
st.caption("Ask anything about the New Jersey Devils, Carolina Hurricanes, or New York Islanders")

st.markdown("""
**Example questions:**
- How are the New Jersey Devils performing this season?
- Who are the top scorers on the Carolina Hurricanes?
- How many points does Jack Hughes have?
- Who is on the Islanders roster?
- How is Sebastian Aho performing this season?
""")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the Devils, Hurricanes, or Islanders..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving context and generating answer..."):
            try:
                answer = ask(prompt)
                st.markdown(answer)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
            except Exception as e:
                error_msg = f"Error generating answer: {str(e)}"
                st.error(error_msg)

st.divider()
st.caption("Data sourced from NHL API and ESPN/Sportsnet RSS feeds. Stats current as of latest data refresh.")