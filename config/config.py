import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ── Groq ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.1-8b-instant"   # free model on Groq

# ── RAG Settings ──────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # free, local
CHUNK_SIZE      = 500
CHUNK_OVERLAP   = 50
TOP_K_RESULTS   = 3

# ── Web Search ────────────────────────────────────────
MAX_SEARCH_RESULTS = 3

# ── Bot Persona ───────────────────────────────────────
BOT_NAME = "HR Policy Assistant"
