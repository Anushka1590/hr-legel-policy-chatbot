import streamlit as st
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from models.llm import get_chatgroq_model
from utils.rag_utils import load_and_process_pdf, create_vector_store, retrieve_relevant_chunks
from utils.search_utils import web_search
from config.config import BOT_NAME

### Helper: Build system prompt

def get_system_prompt(response_mode, vector_store_loaded, use_web_search):
    """Return system prompt based on response mode and available sources"""

    base_prompt = """You are an intelligent HR and Legal Policy Assistant.
Your job is to help employees understand company policies and HR guidelines.

STRICT RULES YOU MUST FOLLOW:
- ONLY answer from the sources explicitly provided to you
- If document context is provided, use ONLY that
- If web search results are provided, use ONLY that
- If NEITHER is available, say: "Please upload a document or enable web search to get accurate answers."
- NEVER use your general training knowledge to answer HR/Legal questions
- NEVER mix sources without clearly labeling them
- Always mention which section of the document your answer comes from
- If the answer is not found in provided context say exactly:
  "This information is not found in the uploaded document. Try enabling web search for more information." """

    if response_mode == "Concise":
        return base_prompt + "\n\nRESPONSE STYLE: Keep responses SHORT (2-4 sentences max)"
    else:
        return base_prompt + "\n\nRESPONSE STYLE: Give DETAILED, thorough responses with full explanation"


### Helper: Get response from LLM
def get_chat_response(chat_model, messages, system_prompt):
    """Get response from the Groq chat model"""
    try:
        formatted_messages = [SystemMessage(content=system_prompt)]

        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            else:
                formatted_messages.append(AIMessage(content=msg["content"]))

        response = chat_model.invoke(formatted_messages)
        return response.content

    except Exception as e:
        return f"❌ Error getting response: {str(e)}"


### Helper: Build enriched query with context

def build_enriched_query(user_query, vector_store, use_web_search):
    """
    Enrich user query with:
    1. Relevant chunks from uploaded documents (RAG)
    2. Web search results (if enabled)
    """
    context_parts = []
    sources_used  = []

    # ── RAG: Retrieve from uploaded documents ──
    if vector_store is not None:
        try:
            doc_context = retrieve_relevant_chunks(vector_store, user_query)
            if doc_context:
                context_parts.append(f"📄 DOCUMENT CONTEXT:\n{doc_context}")
                sources_used.append("📄 Company Documents")
        except Exception as e:
            st.warning(f"RAG retrieval error: {str(e)}")

    # ── Web Search: Only if explicitly enabled ──
    if use_web_search:
        try:
            search_results = web_search(user_query)
            if search_results and "error" not in search_results.lower():
                context_parts.append(f"🌐 WEB SEARCH RESULTS:\n{search_results}")
                sources_used.append("🌐 Web Search")
        except Exception as e:
            st.warning(f"Web search error: {str(e)}")

    # ── Case 1: No document, no web search ──
    if not context_parts:
        no_context_query = f"""The user asked: {user_query}

No document has been uploaded and web search is disabled.
Respond with exactly:
"Please upload an HR/Legal document or enable web search to get accurate answers.
I cannot answer from general knowledge in strict mode." """
        return no_context_query, []

    # ── Case 2: Context available ──
    combined_context = "\n\n".join(context_parts)

    if use_web_search and vector_store is not None:
        instruction = "Answer using BOTH the document context AND web search results provided above."
    elif use_web_search and vector_store is None:
        instruction = "Answer using ONLY the web search results provided above."
    else:
        instruction = """Answer using ONLY the document context provided above.
Web search is DISABLED — do NOT use general knowledge.
If the answer is not in the document context, say:
'This information is not found in the uploaded document. Try enabling web search for more information.'"""

    enriched_query = f"""Answer this question: {user_query}

AVAILABLE CONTEXT:
{combined_context}

STRICT INSTRUCTIONS:
- {instruction}
- Always mention which section of the document your answer came from
- Do NOT add any information from your general training knowledge"""

    return enriched_query, sources_used


### Page: Instructions

def instructions_page():
    """Instructions and setup page"""
    st.title("📋 HR & Legal Policy Assistant")
    st.markdown("### Your intelligent guide to company policies and legal documents")

    st.info("👈 Navigate to the **Chat** page from the sidebar to start chatting!")

    st.markdown("""
    ## 🎯 What This Bot Does
    This chatbot helps employees instantly find answers from:
    - HR Policy Documents (leave policy, code of conduct, etc.)
    - Legal Documents (contracts, compliance guidelines)
    - Real-time web search for labor laws and regulations

    ## 🚀 How to Use
    1. **Go to Chat page** using the sidebar
    2. **Upload your HR/Legal PDF** in the sidebar
    3. **Ask questions** in plain English
    4. **Toggle Web Search** for real-time information
    5. **Switch response mode** between Concise and Detailed

    ## ✨ Features
    - 📄 **RAG**: Answers directly from your uploaded documents
    - 🌐 **Web Search**: Real-time search when docs don't have the answer
    - ⚡ **Concise Mode**: Short, direct answers
    - 📝 **Detailed Mode**: In-depth explanations

    ## 💡 Example Questions
    - *"How many days of annual leave am I entitled to?"*
    - *"What is the policy on remote work?"*
    - *"What are the consequences of breaching the code of conduct?"*
    - *"What does Indian labor law say about overtime pay?"*
    """)



### Page: Chat

def chat_page():
    """Main chat interface"""
    st.title(f"🤖 {BOT_NAME}")

    # ── Initialize session state ──
    if "messages"      not in st.session_state:
        st.session_state.messages      = []
    if "vector_store"  not in st.session_state:
        st.session_state.vector_store  = None
    if "doc_processed" not in st.session_state:
        st.session_state.doc_processed = False

    # ── Sidebar Controls ──
    with st.sidebar:
        st.header("⚙️ Settings")

        # Response Mode Toggle
        st.subheader("📝 Response Mode")
        response_mode = st.radio(
            "Choose response style:",
            ["Concise", "Detailed"],
            index=0,
            help="Concise = short answers | Detailed = in-depth explanations"
        )

        st.divider()

        # Web Search Toggle
        st.subheader("🌐 Web Search")
        use_web_search = st.toggle(
            "Enable Web Search",
            value=False,
            help="Search the web when document does not have the answer"
        )

        st.divider()

        # PDF Upload
        st.subheader("📄 Upload Document")
        uploaded_file = st.file_uploader(
            "Upload HR/Legal PDF",
            type=["pdf"],
            help="Upload your company policy or legal document"
        )

        # Process uploaded PDF
        if uploaded_file is not None:
            if not st.session_state.doc_processed:
                with st.spinner("📚 Processing document..."):
                    try:
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".pdf"
                        ) as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name

                        chunks       = load_and_process_pdf(tmp_path)
                        vector_store = create_vector_store(chunks)

                        os.unlink(tmp_path)

                        if vector_store:
                            st.session_state.vector_store  = vector_store
                            st.session_state.doc_processed = True
                            st.success(f"✅ Processed {len(chunks)} chunks!")
                        else:
                            st.error("❌ Failed to process document.")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.success("✅ Document already loaded!")
                if st.button("📤 Upload New Document"):
                    st.session_state.vector_store  = None
                    st.session_state.doc_processed = False
                    st.rerun()

        st.divider()

        # Clear Chat
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        # Status indicators
        st.divider()
        st.subheader("📊 Status")
        st.write("📄 Document:",
                 "✅ Loaded" if st.session_state.doc_processed else "❌ Not loaded")
        st.write("🌐 Web Search:",
                 "✅ On" if use_web_search else "❌ Off")
        st.write("📝 Mode:", response_mode)

    # ── Initialize LLM ──
    chat_model = get_chatgroq_model()
    if not chat_model:
        st.error("❌ Failed to load AI model. Please check your GROQ_API_KEY in .env file.")
        return

    # ── Display Chat History ──
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ── Chat Input ──
    if prompt := st.chat_input("Ask about HR policies, legal documents..."):

        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching and thinking..."):
                try:
                    enriched_query, sources_used = build_enriched_query(
                        prompt,
                        st.session_state.vector_store,
                        use_web_search
                    )

                    messages_with_context = st.session_state.messages[:-1] + [
                        {"role": "user", "content": enriched_query}
                    ]

                    # ── Updated call with 3 parameters ──
                    system_prompt = get_system_prompt(
                        response_mode,
                        st.session_state.vector_store is not None,
                        use_web_search
                    )

                    response = get_chat_response(
                        chat_model,
                        messages_with_context,
                        system_prompt
                    )

                    if sources_used:
                        st.caption(f"Sources used: {' | '.join(sources_used)}")

                    st.markdown(response)

                except Exception as e:
                    response = f"❌ Error: {str(e)}"
                    st.error(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })


### Main

def main():
    st.set_page_config(
        page_title="HR & Legal Policy Assistant",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    with st.sidebar:
        st.title("🧭 Navigation")
        page = st.radio(
            "Go to:",
            ["Chat", "Instructions"],
            index=0
        )
        st.divider()

    if page == "Instructions":
        instructions_page()
    elif page == "Chat":
        chat_page()


if __name__ == "__main__":
    main()