

import sys
import subprocess
import os
def install_packages():
    """
    Installs the required Python packages using pip. This function is called
    when the script is run with the 'install' argument.
    """
    packages = [
        "fastapi",
        "uvicorn[standard]", 
        "python-multipart",
        "nest_asyncio",
        "pdfplumber",
        "langchain",
        "langchain-huggingface",
        "sentence-transformers",
        "aiofiles",
        "Jinja2",
        "langchain-chroma",
        "langchain-text-splitters" 
    ]
    
    print("--- Starting Installation of Required Packages ---")
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install {package}. See error below.")
            print(e)
            print("\nPlease try installing the package manually and then run the app again.")
            sys.exit(1) # Exit the script if an installation fails

    print("\n--- All packages installed successfully! ---")
    print("You can now run the application with: python pagewise_app.py")




def run_app():
    """
    Defines and runs the main FastAPI application. This is called when the script
    is run without the 'install' argument.
    """
    import nest_asyncio
    import uvicorn
    from fastapi import FastAPI, File, UploadFile, Request, Body
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.templating import Jinja2Templates
    from fastapi.staticfiles import StaticFiles
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter # Import advanced text splitter
    import pdfplumber
    import threading
    import aiofiles
    import logging
    from typing import Dict


    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    nest_asyncio.apply()

    app = FastAPI(
        title="PageWise PDF Q&A",
        description="Upload a PDF and ask questions about its content.",
        version="1.0.0"
    )

    
    os.makedirs("static", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")

    # --- In-Memory Storage & Models ---
    vector_dbs: Dict[str, Chroma] = {}
    SESSION_ID = "default_user"

    try:
        logging.info("Loading HuggingFace embedding model...")
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        logging.info("Embedding model loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load embedding model: {e}")
        embedding_model = None

    # --- HTML Template ---
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DocuVerse</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: 'Inter', sans-serif; }
            .loader { border-top-color: #3498db; animation: spin 1s linear infinite; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body class="bg-gray-100 flex items-center justify-center min-h-screen">
        <div class="bg-white rounded-lg shadow-xl p-8 max-w-2xl w-full">
            <h1 class="text-3xl font-bold text-gray-800 mb-4 text-center">PageWise</h1>
            <p class="text-gray-600 mb-6 text-center">Upload a PDF document to start asking questions.</p>
            <div id="status-message" class="hidden p-4 mb-4 text-sm rounded-lg" role="alert"></div>
            <div class="mb-6">
                <label for="file-upload" class="block mb-2 text-sm font-medium text-gray-700">1. Upload PDF</label>
                <div class="flex items-center space-x-4">
                    <input id="file-upload" name="file" type="file" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" accept=".pdf">
                    <button onclick="uploadPDF()" class="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition duration-200 whitespace-nowrap">Upload</button>
                </div>
            </div>
            <div class="mb-4">
                <label for="question-input" class="block mb-2 text-sm font-medium text-gray-700">2. Ask a Question</label>
                <div class="flex items-center space-x-4">
                    <input type="text" id="question-input" class="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="e.g., What is the main conclusion?">
                    <button onclick="askQuestion()" id="ask-button" class="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50 transition duration-200 flex items-center justify-center">
                        <span id="ask-button-text">Ask</span>
                        <div id="loader" class="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-6 w-6 ml-3 hidden"></div>
                    </button>
                </div>
            </div>
            <div id="answer-container" class="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200 hidden">
                <h3 class="font-semibold text-lg text-gray-800 mb-2">Answer:</h3>
                <div id="answer-text" class="text-gray-700 whitespace-pre-wrap"></div>
            </div>
        </div>
        <script>
            const statusMessage = document.getElementById('status-message');
            function showStatus(message, type = 'success') {
                statusMessage.textContent = message;
                statusMessage.className = 'p-4 mb-4 text-sm rounded-lg'; // Reset classes
                if (type === 'success') {
                    statusMessage.classList.add('bg-green-100', 'text-green-800');
                } else {
                    statusMessage.classList.add('bg-red-100', 'text-red-800');
                }
            }
            async function uploadPDF() {
                const fileInput = document.getElementById('file-upload');
                if (fileInput.files.length === 0) {
                    showStatus('Please select a PDF file first.', 'error');
                    return;
                }
                const formData = new FormData();
                formData.append("file", fileInput.files[0]);
                showStatus('Uploading and processing PDF...', 'success');
                try {
                    const response = await fetch("/upload_pdf", { method: "POST", body: formData });
                    const data = await response.json();
                    if (response.ok) {
                        showStatus(data.message, 'success');
                    } else {
                        showStatus(data.detail || 'An error occurred.', 'error');
                    }
                } catch (error) {
                    showStatus('Failed to connect to the server.', 'error');
                }
            }
            async function askQuestion() {
                const questionInput = document.getElementById('question-input');
                const question = questionInput.value;
                if (!question.trim()) {
                    showStatus('Please enter a question.', 'error');
                    return;
                }
                const askButton = document.getElementById('ask-button'), loader = document.getElementById('loader');
                const askButtonText = document.getElementById('ask-button-text');
                askButton.disabled = true;
                askButtonText.classList.add('hidden');
                loader.classList.remove('hidden');
                try {
                    const response = await fetch("/ask", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ question: question })
                    });
                    const data = await response.json();
                    const answerContainer = document.getElementById('answer-container');
                    const answerText = document.getElementById('answer-text');
                    if (response.ok) {
                        answerText.textContent = data.answer;
                        answerContainer.classList.remove('hidden');
                        statusMessage.className = 'hidden';
                    } else {
                        showStatus(data.detail || data.answer, 'error');
                        answerContainer.classList.add('hidden');
                    }
                } catch (error) {
                    showStatus('Failed to connect to the server.', 'error');
                } finally {
                    askButton.disabled = false;
                    askButtonText.classList.remove('hidden');
                    loader.classList.add('hidden');
                }
            }
        </script>
    </body>
    </html>
    """
    with open("templates/index.html", "w") as f:
        f.write(html_template)

    def load_and_chunk_pdf(file_path: str):
        """
        Extracts text from a PDF and uses a robust recursive splitter to create
        semantically meaningful and consistently sized chunks.
        """
        texts = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        texts.append(page_text)
            
            if not texts:
                return []

            full_text = "\n".join(texts)
            
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,  # Max size of each chunk
                chunk_overlap=200, 
                length_function=len
            )
            
            
            documents = text_splitter.create_documents([full_text])
            logging.info(f"Split PDF into {len(documents)} chunks.")
            return documents
        except Exception as e:
            logging.error(f"Error processing PDF {file_path}: {e}")
            return []

    def create_vectorstore(documents: list[Document]):
        if not embedding_model: raise RuntimeError("Embedding model not available.")
        if not documents: return None
        try:
            return Chroma.from_documents(documents, embedding_model)
        except Exception as e:
            logging.error(f"Failed to create vector store: {e}")
            return None

    @app.get("/", response_class=HTMLResponse)
    async def get_index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.post("/upload_pdf")
    async def upload_pdf(file: UploadFile = File(...)):
        if not file.filename.lower().endswith('.pdf'):
            return JSONResponse(status_code=400, content={"detail": "Invalid file type. Please upload a PDF."})
        
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join("uploads", safe_filename)
        
        try:
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            documents = load_and_chunk_pdf(file_path)
            if not documents:
                return JSONResponse(status_code=400, content={"detail": "Could not extract text from PDF."})

            vector_db = create_vectorstore(documents)
            if not vector_db:
                return JSONResponse(status_code=500, content={"detail": "Failed to create vector store."})
            
            vector_dbs[SESSION_ID] = vector_db
            return JSONResponse(content={"message": f"'{safe_filename}' is ready for questions!"})
        except Exception as e:
            logging.error(f"Error during upload: {e}")
            return JSONResponse(status_code=500, content={"detail": "An internal server error occurred."})

    @app.post("/ask")
    async def ask_question(payload: dict = Body(...)):
        question = payload.get("question")
        if not question:
            return JSONResponse(status_code=400, content={"detail": "Question cannot be empty."})

        vector_db = vector_dbs.get(SESSION_ID)
        if not vector_db:
            return JSONResponse(status_code=404, content={"answer": "Please upload a PDF first."})

        try:
            docs = vector_db.similarity_search(question, k=3)
            if not docs:
                return JSONResponse(content={"answer": "Could not find relevant information."})
            
            context = "\n\n---\n\n".join([doc.page_content for doc in docs])
            answer = f"Based on the document, here are the most relevant sections:\n\n{context}"
            return JSONResponse(content={"answer": answer})
        except Exception as e:
            logging.error(f"Error during search: {e}")
            return JSONResponse(status_code=500, content={"detail": "Error finding an answer."})

    def start_server():
        uvicorn.run(app, host="0.0.0.0", port=8000)

    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    print("--- FastAPI app is running. Access it at http://127.0.0.1:8000 ---")
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n--- Server shutting down ---")


if __name__ == "__main__":
    # Check if the first command-line argument is 'install'
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'install':
        install_packages()
    else:
        run_app()

