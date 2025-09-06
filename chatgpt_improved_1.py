
import streamlit as st
from g4f import Client, Provider
import time

# Page config
st.set_page_config(page_title="AI Chatbot", page_icon="🧠", layout="wide")

# Initialize session state variables
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "is_responding" not in st.session_state:
    st.session_state.is_responding = False

# Initialize client (sync safe)
# Caching the client ensures it's only created once per session.
@st.cache_resource
def get_client():
    """Creates and returns a g4f client."""
    return Client(provider=Provider.MetaAI)

client = get_client()

st.title("AI Powered Chatbot")
# st.write("The chat input will be disabled while the bot is typing.")

# Display conversation history from session state
for message in st.session_state.conversation_history:
    avatar = "🧑" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# User input
# The chat_input is disabled based on the 'is_responding' session state.
user_input = st.chat_input(
    "Type your message...", 
    disabled=st.session_state.is_responding,
    key="chat_input"
)

if user_input:
    # Set the responding flag to True to disable the input
    st.session_state.is_responding = True
    
    # Append user message to history and display it
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # Generate and display AI response with streaming
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        full_response = ""
        
        try:
            # Create a streaming API call
            response_stream = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are a helpful assistant."}] 
                + st.session_state.conversation_history,
                stream=True  # Enable streaming
            )
            
            # Iterate through the stream chunks
            for chunk in response_stream:
                # Check if there is content in the chunk's delta
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content_piece = chunk.choices[0].delta.content
                    full_response += content_piece
                    # Update the container with the latest response and a typing cursor
                    response_container.markdown(full_response + "▌")
            
            # Final update to the container without the cursor
            response_container.markdown(full_response)

        except Exception as e:
            full_response = f"⚠️ An error occurred: {str(e)}"
            response_container.markdown(full_response)
        
        finally:
            # Append the complete AI response to the conversation history
            if full_response:
                st.session_state.conversation_history.append({"role": "assistant", "content": full_response})
            
            # Reset the responding flag to False to re-enable the input
            st.session_state.is_responding = False
            
            # Rerun the app to reflect the state change (input enabled)
            st.rerun()
