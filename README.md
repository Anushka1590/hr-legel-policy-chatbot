# HR & Legal Policy Assistant 🤖

A smart chatbot that helps employees instantly find answers from company HR 
and legal policy documents - without manually searching through lengthy PDFs.

---

## The Problem

Anyone who has worked in a company knows the pain - you need to check your 
leave balance, understand a policy, or clarify something from your contract, 
and you end up digging through a 40-page PDF just to find one paragraph.

This chatbot solves exactly that. Upload your HR or legal document, ask your 
question in plain English, and get an instant answer.

---

## Features

- **RAG (Retrieval-Augmented Generation)** - answers come directly from your 
  uploaded documents, not from the AI's general knowledge
- **Live Web Search** - for questions that go beyond the document (like labor 
  laws, government regulations), the bot can search the web in real time
- **Strict Mode** - the bot won't make things up. If the answer isn't in the 
  document, it says so clearly
- **Concise / Detailed responses** - toggle between short answers and 
  in-depth explanations depending on what you need
- **Multi-turn conversations** - the bot remembers context within a session

---

## Tech Stack

| Component | Tool |
|---|---|
| UI | Streamlit |
| LLM | Groq (llama-3.1-8b-instant) |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) |
| Vector Store | FAISS |
| Web Search | DuckDuckGo Search |
| Document Loader | PyPDF |

---

## Project Structure
```
project/
├── config/
│   └── config.py          # API keys and settings
├── models/
│   ├── llm.py             # Groq LLM setup
│   └── embeddings.py      # HuggingFace embeddings
├── utils/
│   ├── rag_utils.py       # Document loading and vector search
│   └── search_utils.py    # Web search logic
├── app.py                 # Main Streamlit app
└── requirements.txt
```

---

## Running Locally

**1. Clone the repository**
```bash
git clone https://github.com/Anushka1590/hr-legal-policy-chatbot.git
cd hr-legal-policy-chatbot
```

**2. Create and activate virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your API key**

Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_api_key_here
```

**5. Run the app**
```bash
streamlit run app.py
```

---

## How to Use

1. Open the app in your browser
2. Upload an HR or legal policy PDF from the sidebar
3. Wait for the document to process (usually takes a few seconds)
4. Start asking questions in plain English
5. Toggle **Web Search** on for questions not covered in the document
6. Switch between **Concise** and **Detailed** mode as needed

---

## Example Questions to Try

Once you upload an HR policy document, try asking:

- *"How many earned leaves am I entitled to per year?"*
- *"What counts as misconduct?"*
- *"What is the resignation notice period?"*
- *"What are the responsibilities of the HOD?"*

With web search enabled:
- *"What does Indian labor law say about maternity leave?"*
- *"What are the rules for employee termination in India?"*

---

## Deployment

Live demo: **[\[hr-legel-policy-chatbot\]](https://hr-legel-policy-chatbot-pfg4amwbgzzy5rwb2ivpb3.streamlit.app/)**

---

## Known Limitations

- The bot works best with text-based PDFs. Scanned image PDFs may not extract 
  text correctly
- Very large documents (200+ pages) may take longer to process
- Web search depends on DuckDuckGo availability
- Groq free tier has a rate limit of 6000 tokens per minute
