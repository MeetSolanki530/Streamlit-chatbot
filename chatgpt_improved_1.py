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

# Initialize client (using synchronous client to avoid async issues)
@st.cache_resource
def get_client():
    return Client(provider=Provider.MetaAI)

client = get_client()

st.title("AI Powered Chatbot")

# Display conversation history
for message in st.session_state.conversation_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="🧑"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message["content"])

# Show status when processing
if st.session_state.is_processing:
    st.info("🤖 AI is responding... Please wait until the response is complete.")

# Handle user input
user_input = st.chat_input(
    "Type your message..." if not st.session_state.is_processing else "Please wait for the current response to complete...",
    disabled=st.session_state.is_processing
)

if user_input and not st.session_state.is_processing:
    # Only process if not already processing
    # Set processing state immediately
    st.session_state.is_processing = True
    
    # Add user message to history
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    
    # Show user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
    
    # Create response container
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        
        # Show loading state
        response_container.markdown("🤔 Thinking...")
        
        # Prepare messages for API
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Remember context and help the user."}
        ] + st.session_state.conversation_history
        
        try:
            # Get response using synchronous client with streaming
            response_stream = client.chat.completions.create(
                messages=messages,
                stream=True,
            )
            
            full_response = ""
            # Process streaming chunks correctly
            for chunk in response_stream:
                # Extract content from chunk properly
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    if hasattr(choice, 'delta') and choice.delta:
                        content = choice.delta.content
                        if content:
                            full_response += content
                            # Update display with current response + cursor
                            response_container.markdown(full_response + "▌")
                            time.sleep(0.05)  # Small delay for streaming effect if we want
                
                # Check if streaming is finished
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    if chunk.choices[0].finish_reason == 'stop':
                        break
            
            # Remove cursor and show final response
            response_container.markdown(full_response)
            
            # Add response to history
            if full_response.strip():
                st.session_state.conversation_history.append({"role": "assistant", "content": full_response})
            else:
                # Fallback if streaming didn't work
                fallback_response = "I'm here! How can I help you?"
                response_container.markdown(fallback_response)
                st.session_state.conversation_history.append({"role": "assistant", "content": fallback_response})
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            response_container.markdown(error_msg)
            st.session_state.conversation_history.append({"role": "assistant", "content": error_msg})
        
        finally:
            # Reset processing state
            st.session_state.is_processing = False
            time.sleep(0.1)  # Small delay to ensure state is saved
    
    # Rerun to update interface
    st.rerun()