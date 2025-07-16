# Documentation router
"""FastAPI router for documentation endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from ..models.document import Document, DocumentSection, DocumentType
from ..schemas.document import DocumentResponse, DocumentSectionResponse, SearchRequest, SearchResponse
from ..services.document_processor import DocumentProcessor
from ..utils.exceptions import DocumentProcessingError

router = APIRouter(prefix="/docs", tags=["documentation"])


@router.post("/load")
async def load_documents(file_path: str, request: Request) -> JSONResponse:
    """Load documents from a file or directory."""
    try:
        # Check if it's a single file or directory
        if file_path.endswith('.json'):
            document = await request.app.state.doc_processor.load_documents_from_json_file(file_path)
            return JSONResponse({
                "message": "Document loaded successfully",
                "document_id": document.id,
                "sections_count": len(document.sections)
            })
        else:
            documents = await request.app.state.doc_processor.load_documents_from_directory(file_path)
            return JSONResponse({
                "message": f"Loaded {len(documents)} documents",
                "document_ids": [doc.id for doc in documents],
                "total_sections": sum(len(doc.sections) for doc in documents)
            })
            
    except DocumentProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/load-all")
async def load_all_documents(request: Request) -> JSONResponse:
    """Automatically load all documents from the data directory."""
    try:
        # Hardcoded path to the data directory
        data_path = "data"
        documents = await request.app.state.doc_processor.load_documents_from_directory(data_path)
        return JSONResponse({
            "message": f"Loaded {len(documents)} documents from data folder",
            "document_ids": [doc.id for doc in documents],
            "total_sections": sum(len(doc.sections) for doc in documents),
            "data_path": data_path
        })
        
    except DocumentProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/documents")
async def list_documents(request: Request) -> List[DocumentResponse]:
    """List all loaded documents."""
    try:
        doc_processor = request.app.state.doc_processor
        print(f"API DEBUG: /docs/documents called")
        print(f"API DEBUG: doc_processor type: {type(doc_processor)}")
        print(f"API DEBUG: documents count: {len(doc_processor.documents) if hasattr(doc_processor, 'documents') else 'No documents attribute'}")
        
        if hasattr(doc_processor, 'documents'):
            print(f"API DEBUG: documents keys: {list(doc_processor.documents.keys())[:5]}...")  # Show first 5 keys
            documents = [DocumentResponse.from_document(doc) for doc in doc_processor.documents.values() if doc is not None]
            print(f"API DEBUG: Returning {len(documents)} documents")
            return documents
        else:
            print("API DEBUG: doc_processor has no documents attribute")
            return []
    except Exception as e:
        print(f"API DEBUG: Exception in list_documents: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/documents/{document_id}")
async def get_document(document_id: str, request: Request) -> DocumentResponse:
    """Get a specific document by ID."""
    try:
        doc_processor = request.app.state.doc_processor
        document = doc_processor.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return DocumentResponse.from_document(document)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/documents/{document_id}/sections")
async def get_document_sections(request: Request, document_id: str, section_type: Optional[DocumentType] = Query(None, description="Filter by section type")) -> List[DocumentSectionResponse]:
    """Get sections for a specific document."""
    try:
        doc_processor = request.app.state.doc_processor
        document = doc_processor.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        sections = document.sections
        if section_type:
            sections = [s for s in sections if s.section_type == section_type]
        return [
            DocumentSectionResponse(
                id=section.id,
                title=section.title,
                content=section.content,
                file_path=section.file_path,
                line_start=section.line_start,
                line_end=section.line_end,
                section_type=section.section_type,
                metadata=section.metadata,
                created_at=section.created_at,
                updated_at=section.updated_at
            ) for section in sections
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sections/{section_id}")
async def get_section(section_id: str, request: Request) -> DocumentSectionResponse:
    """Get a specific section by ID."""
    try:
        doc_processor = request.app.state.doc_processor
        section = doc_processor.get_section_by_id(section_id)
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
            
        return DocumentSectionResponse(
            id=section.id,
            title=section.title,
            content=section.content,
            file_path=section.file_path,
            line_start=section.line_start,
            line_end=section.line_end,
            section_type=section.section_type,
            metadata=section.metadata,
            created_at=section.created_at,
            updated_at=section.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/search")
async def search_sections(request: Request, search_request: SearchRequest) -> SearchResponse:
    """Search for sections based on query."""
    try:
        doc_processor = request.app.state.doc_processor
        sections = doc_processor.search_sections(
            query=search_request.query,
            limit=search_request.limit or 10
        )
        section_responses = [
            DocumentSectionResponse(
                id=section.id,
                title=section.title,
                content=section.content,
                file_path=section.file_path,
                line_start=section.line_start,
                line_end=section.line_end,
                section_type=section.section_type,
                metadata=section.metadata,
                created_at=section.created_at,
                updated_at=section.updated_at
            ) for section in sections
        ]
        return SearchResponse(
            query=search_request.query,
            results=section_responses,
            total_results=len(section_responses)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sections")
async def list_sections(request: Request, section_type: Optional[DocumentType] = Query(None, description="Filter by section type"), limit: int = Query(20, ge=1, le=100, description="Number of sections to return")) -> List[DocumentSectionResponse]:
    """List all sections with optional filtering."""
    try:
        doc_processor = request.app.state.doc_processor
        if section_type:
            sections = doc_processor.get_sections_by_type(section_type)
        else:
            sections = list(doc_processor.sections.values())
        sections = sections[:limit]
        return [
            DocumentSectionResponse(
                id=section.id,
                title=section.title,
                content=section.content,
                file_path=section.file_path,
                line_start=section.line_start,
                line_end=section.line_end,
                section_type=section.section_type,
                metadata=section.metadata,
                created_at=section.created_at,
                updated_at=section.updated_at
            ) for section in sections
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sections/code")
async def get_code_sections(request: Request) -> List[DocumentSectionResponse]:
    """Get all sections that contain code blocks."""
    try:
        doc_processor = request.app.state.doc_processor
        sections = doc_processor.get_sections_with_code()
        
        return [
            DocumentSectionResponse(
                id=section.id,
                title=section.title,
                content=section.content,
                file_path=section.file_path,
                line_start=section.line_start,
                line_end=section.line_end,
                section_type=section.section_type,
                metadata=section.metadata,
                created_at=section.created_at,
                updated_at=section.updated_at
            ) for section in sections
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")