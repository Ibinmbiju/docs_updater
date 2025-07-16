# Document model
"""Document models for the application."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel


class DocumentType(str, Enum):
    """Document type enumeration."""
    MARKDOWN = "markdown"
    TEXT = "text"
    CODE = "code"


class DocumentSection(BaseModel):
    """Represents a section of a document."""
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


class Document(BaseModel):
    """Complete document with all sections."""
    id: str
    name: str
    file_path: str
    content: str
    sections: List[DocumentSection]
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"