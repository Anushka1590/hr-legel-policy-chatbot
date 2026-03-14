import os
from dotenv import load_dotenv
import streamlit as st

# Load .env for local development
load_dotenv()

def get_api_key():
    """
    Get API key from either:
    1. Streamlit Cloud secrets (when deployed)
    2. .env file (local development)
    """
    try:
        # Try Streamlit secrets first (production)
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        # Fall back to .env (local)
        return os.getenv("GROQ_API_KEY")

# ── Groq ──────────────────────────────────────────────
GROQ_API_KEY = get_api_key()
GROQ_MODEL   = "llama-3.1-8b-instant"

# ── RAG Settings ──────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE      = 500
CHUNK_OVERLAP   = 50
TOP_K_RESULTS   = 3

# ── Web Search ────────────────────────────────────────
MAX_SEARCH_RESULTS = 3

# ── Bot Persona ───────────────────────────────────────
BOT_NAME = "HR Policy Assistant"