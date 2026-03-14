import os
import sys
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS
from models.embeddings import get_embedding_model

def load_and_process_pdf(pdf_path):
    """Load a PDF file and split into chunks"""
    try:
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        chunks = splitter.split_documents(documents)
        return chunks
    
    except Exception as e:
        print(f"Error loading PDF: {str(e)}")
        return []

def create_vector_store(chunks):
    """Create FAISS vector store from document chunks"""
    try:
        embeddings = get_embedding_model()
        if not embeddings:
            raise ValueError("Embedding model failed to load.")
        
        vector_store = FAISS.from_documents(chunks, embeddings)
        return vector_store
    
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None

def retrieve_relevant_chunks(vector_store, query):
    """Retrieve top K relevant chunks for a query"""
    try:
        results = vector_store.similarity_search(query, k=TOP_K_RESULTS)
        # Combine chunks into single context string
        context = "\n\n".join([doc.page_content for doc in results])
        return context
    
    except Exception as e:
        print(f"Error retrieving chunks: {str(e)}")
        return ""