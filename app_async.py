import streamlit as st
from g4f import AsyncClient,Provider
import asyncio

st.set_page_config(
    page_title="G4F AI Chatbot",
    page_icon="🧠",
)

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


# --- Event loop fix ---
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)



client = AsyncClient(provider=Provider.MetaAI)




st.header("AI Powered Chatbot")


question = st.text_input("Enter Your Question:- ")


async def get_response():
    st.session_state.conversation_history.append({"role" : "user","content" : question})
    response = await client.chat.completions.create(
    messages=[{"role" : "system","content" : f"""You are helpful assistant Help User to resolve their Query.  Help the user resolve their queries while remembering context."""}] + st.session_state.conversation_history,
        stream=False,
        # model=""
        )
    
    st.markdown(response.choices[0].message.content)
    st.session_state.conversation_history.append({"role" : "system","content" : response.choices[0].message.content})
    print(st.session_state.conversation_history)
    return None



if st.button(label="Get AI Response"):
    st.session_state.loop.run_until_complete(get_response())

st.write("### Conversation History")
for message in st.session_state.conversation_history:
    if message["role"] == "user" :
        with st.chat_message(name="human"):
            st.markdown(message["content"])
    elif message["role"] == "system":
        with st.chat_message(name="assistant"):
            st.markdown(message["content"])
