import streamlit as st
from langchain_g4f.text import ChatG4F
from g4f import Provider
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser

st.title("WebBase RAG Chatbot")


llm = ChatG4F(provider=Provider.MetaAI)

# Initialize session state
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

web_link = st.text_input("Provide Link for RAG Base Chat:- ")

def generate_vector_store(web_link):
    loader = WebBaseLoader(web_path=web_link).load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)


    documents_splitted = splitter.split_documents(loader)

    vector_store = FAISS.from_documents(documents_splitted,
                                        embedding=HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2"))

    return vector_store



if st.button("Generate Context Embeddings"):
    with st.spinner("Generating Embedding..."):
        st.session_state.vectorstore = generate_vector_store(web_link)
    st.success("Context embeddings generated!")

# Footer note
st.markdown(
    """
    <div style="position:fixed; bottom:0; left:0; width:100%; 
                background: linear-gradient(90deg, #1e3c72, #2a5298); 
                padding:6px; text-align:center; border-top:1px solid #444;">
        <marquee behavior="scroll" direction="left" scrollamount="4" 
                 style="color:white; font-size:14px; font-weight:bold;">
            ⚡ Note: This app uses free AI models, so responses may take some time. Please be patient. ⚡
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.vectorstore:

    Query = st.text_input("What is ur question??")


    prompt = PromptTemplate.from_template("""
    You are helpful assistant who are Responsible to provide response to user query based on provided context only.
    Ensure User Can Use alternate words for context for example user can use link, context, content, passage consider all this about context provided.
    Always Directly response in clear detailed With Professional Tone.

    <context>
    {context}
    </context>

    User Query :- {input}
    Answer :                                    
    """)

    if st.button("Get Response"):
        with st.spinner("Generating Response..."):   
            if "vectorstore" not in st.session_state:
                st.error("Please generate embeddings first!")
            else:
                retriever = st.session_state.vectorstore.as_retriever()
            
            prompt_formatted = prompt.format(context = st.session_state.vectorstore.as_retriever(),input = Query)
            
            chain = (
            {
                "context": lambda x: retriever.invoke(x["question"]),
                "input": lambda x: x["question"],
            }
            | prompt
            | llm
            | StrOutputParser()
        )

            response  = chain.invoke({"question" : Query})
            
            st.markdown(response)

else:
    st.info("ℹ️ Please enter a URL and generate embeddings first.")


