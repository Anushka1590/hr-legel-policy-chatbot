from langchain_community.embeddings import HuggingFaceEmbeddings
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import EMBEDDING_MODEL

def get_embedding_model():
    """Initialize and return HuggingFace embedding model (free, runs locally)"""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},   # runs on CPU, no GPU needed
            encode_kwargs={"normalize_embeddings": True}
        )
        return embeddings
    
    except Exception as e:
        print(f"Error initializing embedding model: {str(e)}")
        return None