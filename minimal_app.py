#!/usr/bin/env python3
"""
Minimal version of the AI Calling Agent application.

This is a simplified version with minimal dependencies for demonstration purposes.
"""

import os
import time
import json
import uvicorn
import shutil
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import document processor
try:
    from app.document_processor import get_document_processor
    document_processor = get_document_processor()
    DOCUMENT_PROCESSOR_AVAILABLE = True
except ImportError:
    print("Warning: Document processor not available. Some features will be disabled.")
    DOCUMENT_PROCESSOR_AVAILABLE = False

# Create necessary directories
os.makedirs("app/templates", exist_ok=True)
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)
os.makedirs("app/uploads", exist_ok=True)
os.makedirs("app/knowledge", exist_ok=True)

# Create a simple FastAPI app
app = FastAPI(
    title="AI Calling Agent (Minimal)",
    description="A simplified version of the AI Calling Agent",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Basic API endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "AI Calling Agent minimal demo is running",
        "document_processor": DOCUMENT_PROCESSOR_AVAILABLE
    }

# TTS demo endpoint
@app.get("/api/tts/demo")
async def tts_demo():
    """TTS demo information endpoint."""
    return {
        "message": "TTS demo mode active",
        "supported_languages": ["en", "hi", "mr", "te"],
        "tts_engines": ["google", "indic"]
    }

# Background task to process uploaded document
def process_document_task(document_path: str):
    """Process a document in the background."""
    if DOCUMENT_PROCESSOR_AVAILABLE:
        try:
            document_processor.process_document(document_path)
            print(f"Document processed: {document_path}")
        except Exception as e:
            print(f"Error processing document {document_path}: {str(e)}")

# Document upload endpoint
@app.post("/api/upload/document")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: str = Form(None),
    category: str = Form("general")
):
    """
    Upload a document (PDF, Word, Excel) to use as knowledge base.
    
    This endpoint accepts document uploads and stores them for knowledge extraction.
    """
    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".xlsx", ".xls", ".csv", ".txt"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create a unique filename
    timestamp = int(time.time())
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join("app/uploads", safe_filename)
    
    # Save the uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Store metadata
    metadata = {
        "filename": file.filename,
        "stored_filename": safe_filename,
        "path": file_path,
        "description": description or "",
        "category": category,
        "upload_time": timestamp,
        "size": os.path.getsize(file_path),
        "extension": file_ext
    }
    
    # Save metadata to a JSON file
    metadata_path = os.path.join("app/knowledge", f"{timestamp}_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Process the document in the background
    if DOCUMENT_PROCESSOR_AVAILABLE:
        background_tasks.add_task(process_document_task, file_path)
    
    return {
        "status": "success",
        "message": "Document uploaded successfully",
        "document_id": str(timestamp),
        "filename": file.filename,
        "category": category,
        "processing": DOCUMENT_PROCESSOR_AVAILABLE
    }

# Get uploaded documents endpoint
@app.get("/api/documents")
async def get_documents():
    """Get a list of uploaded documents."""
    documents = []
    
    # Read metadata files from the knowledge directory
    metadata_files = Path("app/knowledge").glob("*_metadata.json")
    
    for metadata_file in metadata_files:
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                
            # Check if the file still exists
            if os.path.exists(metadata["path"]):
                documents.append({
                    "id": metadata_file.stem.split("_")[0],
                    "filename": metadata["filename"],
                    "description": metadata["description"],
                    "category": metadata["category"],
                    "upload_time": metadata["upload_time"],
                    "size": metadata["size"],
                    "extension": metadata["extension"]
                })
        except Exception as e:
            print(f"Error reading metadata file {metadata_file}: {str(e)}")
    
    # Sort by upload time (newest first)
    documents.sort(key=lambda x: x["upload_time"], reverse=True)
    
    return {"documents": documents}

# Delete document endpoint
@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete an uploaded document."""
    metadata_path = os.path.join("app/knowledge", f"{document_id}_metadata.json")
    
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Read metadata to get the file path
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        # Delete the document file
        if os.path.exists(metadata["path"]):
            os.remove(metadata["path"])
        
        # Delete the metadata file
        os.remove(metadata_path)
        
        return {"status": "success", "message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

# Process all documents endpoint
@app.post("/api/documents/process")
async def process_all_documents(background_tasks: BackgroundTasks):
    """Process all uploaded documents."""
    if not DOCUMENT_PROCESSOR_AVAILABLE:
        raise HTTPException(status_code=400, detail="Document processor not available")
    
    # Add background task to process all documents
    background_tasks.add_task(lambda: document_processor.process_all_documents())
    
    return {
        "status": "success",
        "message": "Document processing started in the background"
    }

# Get document summary endpoint
@app.get("/api/documents/{document_id}/summary")
async def get_document_summary(document_id: str):
    """Get a summary of a document."""
    if not DOCUMENT_PROCESSOR_AVAILABLE:
        raise HTTPException(status_code=400, detail="Document processor not available")
    
    summary = document_processor.get_document_summary(document_id)
    
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    
    return summary

# Question answering endpoint
@app.post("/api/knowledge/question")
async def answer_question(question: str = Form(...), language: str = Form("en")):
    """
    Answer a question using the knowledge base.
    
    This endpoint uses the document processor to find relevant information
    and generate an answer to the question.
    """
    if not DOCUMENT_PROCESSOR_AVAILABLE:
        raise HTTPException(status_code=400, detail="Document processor not available")
    
    # Process all documents if not already processed
    if not document_processor.processed_knowledge:
        document_processor.process_all_documents()
    
    # Get answer from knowledge base
    result = document_processor.get_answer_from_knowledge_base(question)
    
    # Add the original question to the result
    result["question"] = question
    result["language"] = language
    
    return result

# Call simulation endpoint
@app.post("/api/call/simulate")
async def simulate_call(
    phone_number: str = Query(..., description="Phone number to call"),
    language: str = Query("en", description="Language for the call"),
    engine: str = Query("auto", description="TTS engine to use")
):
    """
    Simulate a phone call.
    
    This endpoint simulates a phone call with the specified parameters.
    In a real implementation, this would connect to a telephony service.
    """
    # Validate language
    if language not in ["en", "hi", "mr", "te"]:
        raise HTTPException(status_code=400, detail="Unsupported language")
    
    # Validate engine
    if engine not in ["auto", "google", "indic"]:
        raise HTTPException(status_code=400, detail="Unsupported TTS engine")
    
    # Simulate call processing time
    time.sleep(1)
    
    # Return call simulation result
    return {
        "call_id": f"sim-{int(time.time())}",
        "status": "completed",
        "phone_number": phone_number,
        "language": language,
        "engine": engine,
        "duration": 15,  # seconds
        "message": f"Call simulation completed successfully using {engine} TTS engine in {language} language."
    }

# Root endpoint redirects to chat
@app.get("/")
async def root():
    """Root endpoint that redirects to chat interface."""
    return RedirectResponse(url="/chat")

# Chat endpoint
@app.get("/chat", response_class=HTMLResponse)
async def chat():
    """Chat interface endpoint."""
    try:
        with open("app/templates/chat.html", "r") as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return """
        <html>
            <head><title>AI Calling Agent</title></head>
            <body>
                <h1>Chat interface not found</h1>
                <p>Please make sure app/templates/chat.html exists.</p>
            </body>
        </html>
        """

# API documentation endpoint
@app.get("/api/docs", response_class=HTMLResponse)
async def api_docs():
    """API documentation endpoint."""
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AI Calling Agent - API Documentation</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                h1, h2, h3 {
                    color: #4a6fa5;
                }
                .endpoint {
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    border-left: 4px solid #4a6fa5;
                }
                .method {
                    font-weight: bold;
                    color: #4a6fa5;
                }
                pre {
                    background-color: #f9f9f9;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }
                code {
                    font-family: monospace;
                }
            </style>
        </head>
        <body>
            <h1>AI Calling Agent API Documentation</h1>
            
            <div class="endpoint">
                <h2><span class="method">GET</span> /api/health</h2>
                <p>Health check endpoint to verify the service is running.</p>
                <h3>Response:</h3>
                <pre><code>{
  "status": "ok",
  "message": "AI Calling Agent minimal demo is running",
  "document_processor": true
}</code></pre>
            </div>
            
            <div class="endpoint">
                <h2><span class="method">GET</span> /api/tts/demo</h2>
                <p>Get information about the TTS demo capabilities.</p>
                <h3>Response:</h3>
                <pre><code>{
  "message": "TTS demo mode active",
  "supported_languages": ["en", "hi", "mr", "te"],
  "tts_engines": ["google", "indic"]
}</code></pre>
            </div>
            
            <div class="endpoint">
                <h2><span class="method">POST</span> /api/upload/document</h2>
                <p>Upload a document (PDF, Word, Excel) to use as knowledge base.</p>
                <h3>Parameters:</h3>
                <ul>
                    <li><code>file</code> (required): The document file to upload</li>
                    <li><code>description</code> (optional): Description of the document</li>
                    <li><code>category</code> (optional, default: "general"): Category for the document</li>
                </ul>
                <h3>Response:</h3>
                <pre><code>{
  "status": "success",
  "message": "Document uploaded successfully",
  "document_id": "1234567890",
  "filename": "company_info.pdf",
  "category": "general",
  "processing": true
}</code></pre>
            </div>
            
            <div class="endpoint">
                <h2><span class="method">GET</span> /api/documents</h2>
                <p>Get a list of uploaded documents.</p>
                <h3>Response:</h3>
                <pre><code>{
  "documents": [
    {
      "id": "1234567890",
      "filename": "company_info.pdf",
      "description": "Company information and services",
      "category": "general",
      "upload_time": 1234567890,
      "size": 1024000,
      "extension": ".pdf"
    }
  ]
}</code></pre>
            </div>
            
            <div class="endpoint">
                <h2><span class="method">DELETE</span> /api/documents/{document_id}</h2>
                <p>Delete an uploaded document.</p>
                <h3>Parameters:</h3>
                <ul>
                    <li><code>document_id</code> (required): ID of the document to delete</li>
                </ul>
                <h3>Response:</h3>
                <pre><code>{
  "status": "success",
  "message": "Document deleted successfully"
}</code></pre>
            </div>
            
            <div class="endpoint">
                <h2><span class="method">POST</span> /api/documents/process</h2>
                <p>Process all uploaded documents.</p>
                <h3>Response:</h3>
                <pre><code>{
  "status": "success",
  "message": "Document processing started in the background"
}</code></pre>
            </div>
            
            <div class="endpoint">
                <h2><span class="method">GET</span> /api/documents/{document_id}/summary</h2>
                <p>Get a summary of a document.</p>
                <h3>Parameters:</h3>
                <ul>
                    <li><code>document_id</code> (required): ID of the document</li>
                </ul>
                <h3>Response:</h3>
                <pre><code>{
  "doc_id": "1234567890",
  "filename": "company_info.pdf",
  "description": "Company information and services",
  "category": "general",
  "upload_time": 1234567890,
  "sections": 5,
  "section_titles": ["Introduction", "Services", "Pricing", "Contact", "Technology"],
  "text_length": 15000
}</code></pre>
            </div>
            
            <div class="endpoint">
                <h2><span class="method">POST</span> /api/knowledge/question</h2>
                <p>Answer a question using the knowledge base.</p>
                <h3>Parameters:</h3>
                <ul>
                    <li><code>question</code> (required): The question to answer</li>
                    <li><code>language</code> (optional, default: "en"): Language for the answer</li>
                </ul>
                <h3>Response:</h3>
                <pre><code>{
  "question": "What services do you offer?",
  "answer": "Our company offers a range of AI-powered communication solutions...",
  "confidence": 0.85,
  "sources": ["company_info.pdf - Services", "services.docx - Features"],
  "question_type": "services",
  "language": "en"
}</code></pre>
            </div>
            
            <div class="endpoint">
                <h2><span class="method">POST</span> /api/call/simulate</h2>
                <p>Simulate a phone call with text-to-speech capabilities.</p>
                <h3>Parameters:</h3>
                <ul>
                    <li><code>phone_number</code> (required): Phone number to call</li>
                    <li><code>language</code> (optional, default: "en"): Language for the call (en, hi, mr, te)</li>
                    <li><code>engine</code> (optional, default: "auto"): TTS engine to use (auto, google, indic)</li>
                </ul>
                <h3>Response:</h3>
                <pre><code>{
  "call_id": "sim-1234567890",
  "status": "completed",
  "phone_number": "+1234567890",
  "language": "en",
  "engine": "auto",
  "duration": 15,
  "message": "Call simulation completed successfully using auto TTS engine in en language."
}</code></pre>
            </div>
            
            <p>For interactive API documentation, visit <a href="/docs">/docs</a> (Swagger UI) or <a href="/redoc">/redoc</a> (ReDoc).</p>
        </body>
    </html>
    """

# Run the application directly if this script is executed
if __name__ == "__main__":
    print("Starting minimal AI Calling Agent demo on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) 