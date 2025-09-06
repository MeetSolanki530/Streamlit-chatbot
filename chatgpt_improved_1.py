import streamlit as st
from g4f import Client, Provider
import time

# Page config
st.set_page_config(page_title="AI Chatbot", page_icon="🧠", layout="wide")

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Initialize client
@st.cache_resource
def get_client():
    return Client(provider=Provider.MetaAI)

client = get_client()

st.title("AI Powered Chatbot")

# Display conversation history
for message in st.session_state.conversation_history:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Show status when processing
if st.session_state.is_processing:
    st.info("🤖 AI is responding... Please wait...")

# User input (disabled while bot is processing)
user_input = st.chat_input(
    "Type your message...",
    disabled=st.session_state.is_processing
)

if user_input and not st.session_state.is_processing:
    # Mark as processing
    st.session_state.is_processing = True

    # Add user message
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # Bot response container
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        response_container.markdown("🤔 Thinking...")

        # Prepare messages
        messages = [{"role": "system", "content": "You are a helpful assistant."}] + st.session_state.conversation_history
        full_response = ""

        try:
            # Streaming response
            response_stream = client.chat.completions.create(messages=messages, stream=True)

            for chunk in response_stream:
                try:
                    if hasattr(chunk, "choices") and chunk.choices:
                        choice = chunk.choices[0]
                        if hasattr(choice, "delta") and choice.delta:
                            content = getattr(choice.delta, "content", None)
                            if content:
                                full_response += content
                                response_container.markdown(full_response + "▌")
                except Exception:
                    continue  # Ignore bad chunks safely

            # Final response cleanup
            if not full_response.strip():
                full_response = "⚠️ Sorry, I couldn't generate a response."
            response_container.markdown(full_response)

            # Add assistant message
            st.session_state.conversation_history.append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_msg = f"⚠️ Error: {str(e)}"
            response_container.markdown(error_msg)
            st.session_state.conversation_history.append({"role": "assistant", "content": error_msg})

        finally:
            # Always reset state
            st.session_state.is_processing = False
            time.sleep(0.1)
            st.rerun()
