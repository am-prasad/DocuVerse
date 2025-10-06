PageWise: PDF Q&A Application
PageWise is a simple yet powerful web application that allows you to have a conversation with your PDF documents. Built with Python, FastAPI, and LangChain, it provides a clean interface to upload a PDF, process its content, and ask questions to receive relevant answers directly from the text.

This project serves as an excellent starting point for building more complex Retrieval-Augmented Generation (RAG) systems.

Features
Easy PDF Upload: A simple, user-friendly interface to upload any PDF document.

Intelligent Text Processing: Automatically extracts text and uses an advanced algorithm (RecursiveCharacterTextSplitter) to break it down into meaningful, semantically-aware chunks.

State-of-the-Art Embeddings: Utilizes HuggingFace's all-MiniLM-L6-v2 model to generate powerful vector embeddings for the text chunks.

In-Memory Vector Store: Uses ChromaDB to create a fast, in-memory vector database for efficient similarity searches.

Interactive Q&A: Ask questions and get the most relevant text snippets from the document as answers.

All-in-One Script: The entire application, including dependency installation, is contained within a single Python file for maximum portability.

Technology Stack
Backend: FastAPI, Uvicorn

AI/ML: LangChain, LangChain-HuggingFace, Sentence-Transformers, ChromaDB

PDF Parsing: pdfplumber

Frontend: HTML, Tailwind CSS, Vanilla JavaScript

How It Works
The application follows a simple Retrieval-Augmented Generation (RAG) pipeline:

Upload & Parse: The user uploads a PDF file through the web interface. pdfplumber reads the file and extracts all the raw text.

Chunking: The extracted text is passed to LangChain's RecursiveCharacterTextSplitter, which divides the long text into smaller, overlapping chunks. This is crucial for isolating relevant context.

Embedding: Each text chunk is converted into a numerical vector (an embedding) using the all-MiniLM-L6-v2 sentence transformer model. These embeddings capture the semantic meaning of the text.

Indexing: The chunks and their corresponding embeddings are stored in a Chroma vector database in the server's memory.

Retrieval: When the user asks a question, it is also converted into an embedding. The application then performs a similarity search in the vector database to find the text chunks with embeddings most similar to the question's embedding.

Response: The content of the top 3 most relevant chunks is formatted and returned to the user as the answer.

Setup and Usage
Getting PageWise up and running is straightforward.

Prerequisites
Python 3.7+

1. Install Dependencies
The script comes with a built-in installer. Open your terminal, navigate to the directory where you saved pagewise_app.py, and run:

python pagewise_app.py install

This command will read the list of required packages and install them using pip.

2. Run the Application
Once the dependencies are installed, start the web server by running the same file without any arguments:

python pagewise_app.py

You will see a confirmation that the server is running.

3. Access the Application
Open your web browser and navigate to:

http://127.0.0.1:8000

You can now upload a PDF and start asking questions!

Future Improvements
Integrate a Large Language Model (LLM): Instead of just returning the raw text chunks, feed the retrieved context and the user's question to an LLM (like a model from the Gemini family) to generate a more natural, human-like answer.

Support for More File Types: Extend the application to handle other document formats like .docx, .txt, and .md.

Persistent Storage: Implement a persistent vector database (e.g., saving ChromaDB to disk) so that processed documents don't have to be re-indexed every time the server restarts.

User Sessions: Add session management to allow multiple users to work with different documents simultaneously.