from langchain_groq import ChatGroq
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import GROQ_API_KEY, GROQ_MODEL

def get_chatgroq_model():
    """Initialize and return Groq chat model"""
    try:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing. Please check your .env file.")
        
        model = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=0.7
        )
        return model
    
    except Exception as e:
        print(f"Error initializing Groq model: {str(e)}")
        return None