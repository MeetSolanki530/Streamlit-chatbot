import streamlit as st
import asyncio
from g4f import AsyncClient, Provider

# Page config
st.set_page_config(page_title="G4F AI Chatbot", page_icon="🧠", layout="wide")

# Session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)

client = AsyncClient(provider=Provider.MetaAI)

st.title("🧠 AI Powered Chatbot")

# --- Display conversation history ---
for message in st.session_state.conversation_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="🧑"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message["content"])

# --- Async AI response ---
async def get_response(user_input: str):
    # Store user message
    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    # Show user bubble immediately
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # Placeholder for streaming response
    response_container = st.empty()
    response = ""

    async for chunk in client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Remember context and help the user."}
        ]
        + st.session_state.conversation_history,
        stream=True,
    ):
        if hasattr(chunk, "choices"):
            delta = chunk.choices[0].delta.content
            if delta:
                response += delta
                with response_container.container():
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(response)

    # Save full response
    st.session_state.conversation_history.append({"role": "assistant", "content": response})

# --- Chat input at bottom ---
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.loop.run_until_complete(get_response(user_input))
    st.rerun()
