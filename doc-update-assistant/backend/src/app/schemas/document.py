"""Document schemas for API responses."""

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel

from ..models.document import Document, DocumentSection, DocumentType


class DocumentSectionResponse(BaseModel):
    """Document section response schema."""
    id: str
    title: str
    content: str
    file_path: str
    line_start: int
    line_end: int
    section_type: DocumentType
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class DocumentResponse(BaseModel):
    """Document response schema."""
    id: str
    name: str
    file_path: str
    content: str = ""
    sections_count: int
    version: str = "1.0.0"
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}
    
    @classmethod
    def from_document(cls, document: Document) -> "DocumentResponse":
        """Create response from document model."""
        return cls(
            id=document.id,
            name=document.name,
            file_path=document.file_path,
            content=document.content,
            sections_count=len(document.sections),
            version=document.version,
            created_at=document.created_at,
            updated_at=document.updated_at,
            metadata=document.metadata
        )


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str
    limit: int = 10


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    results: List[DocumentSectionResponse]
    total_results: int


class DocumentDetailResponse(DocumentResponse):
    """Detailed document response schema."""
    content: str
    sections: List[DocumentSectionResponse]
    
    @classmethod
    def from_document(cls, document: Document) -> "DocumentDetailResponse":
        """Create detailed response from document model."""
        return cls(
            id=document.id,
            name=document.name,
            file_path=document.file_path,
            content=document.content,
            sections=[DocumentSectionResponse(**section.dict()) for section in document.sections],
            sections_count=len(document.sections),
            version=document.version,
            created_at=document.created_at,
            updated_at=document.updated_at,
            metadata=document.metadata
        )


class DocumentListResponse(BaseModel):
    """Document list response schema."""
    documents: List[DocumentResponse]
    total: int