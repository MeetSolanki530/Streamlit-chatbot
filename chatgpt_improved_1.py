import streamlit as st
from g4f import Client, Provider

# Page config
st.set_page_config(page_title="AI Chatbot", page_icon="🧠", layout="wide")

# Initialize session state variables
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "is_responding" not in st.session_state:
    st.session_state.is_responding = False

# Initialize client (sync safe)
@st.cache_resource
def get_client():
    """Creates and returns a g4f client."""
    return Client(provider=Provider.MetaAI)

client = get_client()

st.title("AI Powered Chatbot")

# Display conversation history
for message in st.session_state.conversation_history:
    avatar = "🧑" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# User input
user_input = st.chat_input(
    "Type your message...",
    disabled=st.session_state.is_responding,
    key="chat_input"
)

if user_input:
    # Disable input while responding
    st.session_state.is_responding = True

    # Append user message
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # AI response (non-streaming)
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        try:
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are a helpful assistant."}]
                + st.session_state.conversation_history,
                stream=False
            )
            full_response = response.choices[0].message.content
            response_container.markdown(full_response)

        except Exception as e:
            full_response = f"⚠️ An error occurred: {str(e)}"
            response_container.markdown(full_response)

        # Save to conversation history
        if full_response:
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": full_response}
            )

    # Re-enable input
    st.session_state.is_responding = False
    st.rerun()
