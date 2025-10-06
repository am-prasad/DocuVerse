🧠 PageWise — Conversational PDF Q&A App

Talk to your PDFs!
PageWise is a simple yet powerful web app built with FastAPI, LangChain, and HuggingFace that lets you upload PDFs, ask questions, and get instant, contextually relevant answers — all directly from your document.

This project is a clean and compact example of a Retrieval-Augmented Generation (RAG) system — perfect for learning, extending, or integrating into your own projects.

✨ Features

✅ Easy PDF Upload – Drag, drop, and go.
🧩 Smart Text Chunking – Uses LangChain’s RecursiveCharacterTextSplitter for semantic chunking.
🤖 Powerful Embeddings – Backed by HuggingFace’s all-MiniLM-L6-v2 sentence transformer.
⚡ Fast In-Memory Search – Efficient vector similarity via ChromaDB.
💬 Interactive Q&A – Ask questions and get precise snippets from your PDF.
📦 Portable Setup – Everything in one Python file — install, run, and explore.

🏗️ Tech Stack
Layer	Tools Used
Backend	FastAPI, Uvicorn
AI/ML	LangChain, Sentence-Transformers, ChromaDB
PDF Parsing	pdfplumber
Frontend	HTML, Tailwind CSS, Vanilla JavaScript
⚙️ How It Works

PageWise follows a streamlined RAG pipeline:

📄 Upload & Parse
Upload a PDF → pdfplumber extracts raw text.

✂️ Chunking
Text is split into meaningful overlapping chunks using LangChain’s RecursiveCharacterTextSplitter.

🧬 Embedding
Each chunk is transformed into a semantic vector using HuggingFace’s all-MiniLM-L6-v2 model.

🧠 Indexing
The chunks and their embeddings are stored in ChromaDB, an in-memory vector database.

🔍 Retrieval
Your question is embedded → compared against stored chunks → top matches are retrieved.

💡 Response
The most relevant text snippets are returned as your answer!

🚀 Getting Started
🧩 Prerequisites

Python 3.7+

1️⃣ Install Dependencies

Run the app in install mode to automatically fetch dependencies:

python pagewise_app.py install

2️⃣ Launch the App

Start the FastAPI server:

python pagewise_app.py

3️⃣ Access in Browser

Navigate to:

http://127.0.0.1:8000


Upload a PDF and start chatting with it! 🎉