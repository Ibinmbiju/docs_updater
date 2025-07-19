"""Main FastAPI application."""

from dotenv import load_dotenv
import os
import asyncio
import traceback
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse

try:
    from .config import settings
    from .routers import documentation, suggestions
    from .utils.exceptions import DocumentUpdateException
    from .services.document_processor import DocumentProcessor
    from .services.ai_service import AIService
        
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback configuration
    class Settings:
        app_name = "Documentation Update Assistant"
        app_version = "0.1.0"
        debug = False
        allowed_origins = ["http://localhost:3000", "http://localhost:8000"]
        openai_api_key = None
    
    settings = Settings()
    
    # Import AIService in fallback too
    try:
        from .services.ai_service import AIService
    except ImportError:
        AIService = None
    
    # Also try to import DocumentProcessor
    try:
        from .services.document_processor import DocumentProcessor
    except ImportError:
        DocumentProcessor = None


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered documentation update assistant with GitHub-like diff functionality",
    default_response_class=ORJSONResponse
)

# Initialize document processor (file-based with pickle embeddings)
print("INFO: Using file-based document processor with pickle embeddings")
if DocumentProcessor:
    app.state.doc_processor = DocumentProcessor()
    print("SUCCESS: Document processor initialized")
else:
    app.state.doc_processor = None
    print("ERROR: DocumentProcessor unavailable")

if AIService:
    app.state.ai_service = AIService()
else:
    app.state.ai_service = None
    print("WARNING: AIService unavailable - suggestions will not work")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (only if successfully imported)
try:
    if 'documentation' in locals() and 'suggestions' in locals():
        app.include_router(documentation.router)
        app.include_router(suggestions.router)
        
        # Exception handlers
        if 'DocumentUpdateException' in locals():
            @app.exception_handler(DocumentUpdateException)
            async def document_update_exception_handler(request, exc):
                """Handle document update exceptions."""
                return JSONResponse(
                    status_code=400,
                    content={"error": str(exc), "type": exc.__class__.__name__}
                )
    else:
        print("Routers not available - running in minimal mode")
except Exception as e:
    print(f"Error setting up routers: {e}")


# Auto-load documents on startup

async def load_documents_background():
    """Load documents in the background without blocking startup."""
    try:
        if not app.state.doc_processor:
            print("[ERROR] Document processor not available. Suggestions will not work.")
            return
            
        data_path = "data"
        if os.path.exists(data_path) and os.path.isdir(data_path):
            print(f"Auto-loading documents from {data_path}...")
            # Add timeout to prevent hanging
            documents = await asyncio.wait_for(
                app.state.doc_processor.load_documents_from_directory(data_path),
                timeout=120.0  # 2 minutes timeout
            )
            if not documents:
                print("[ERROR] No documents loaded from data directory. Suggestions will not work.")
            else:
                print(f"Auto-loaded {len(documents)} documents with {sum(len(doc.sections) for doc in documents)} sections")
        else:
            print(f"[ERROR] Data directory '{data_path}' not found - documents will need to be loaded manually. Suggestions will not work.")
    except asyncio.TimeoutError:
        print("[ERROR] Document loading timed out after 2 minutes. Documents will need to be loaded manually.")
    except Exception as e:
        print(f"Could not auto-load documents: {e}")
        print("[ERROR] Documents will need to be loaded manually. Suggestions will not work.")

@app.on_event("startup")
async def startup_event():
    """Fast startup - launch document loading in background with Redis."""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OpenAI API key not configured. AI suggestions will be disabled.")
    
    # Start document loading in background (non-blocking with timeout)
    asyncio.create_task(load_documents_background())
    print("Application started - documents loading in background with pickle embeddings...")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )