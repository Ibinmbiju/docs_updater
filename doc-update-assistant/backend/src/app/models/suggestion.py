# Suggestion model
"""Suggestion models for the application."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SuggestionStatus(str, Enum):
    """Suggestion status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"


class SuggestionType(str, Enum):
    """Suggestion type enumeration."""
    UPDATE = "update"
    DELETE = "delete"
    ADD = "add"
    MOVE = "move"


class DiffHunk(BaseModel):
    """Represents a single diff hunk (GitHub-style)."""
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    old_lines: List[str]
    new_lines: List[str]
    context_before: List[str] = []
    context_after: List[str] = []


class UpdateSuggestion(BaseModel):
    """Represents a suggestion to update documentation."""
    id: str
    document_id: str
    section_id: str
    title: str
    description: str
    
    # GitHub-like diff information
    diff_hunks: List[DiffHunk]
    original_content: str
    suggested_content: str
    
    # Metadata
    suggestion_type: SuggestionType
    status: SuggestionStatus = SuggestionStatus.PENDING
    confidence_score: float = 0.0
    
    # Tracking
    created_at: datetime
    updated_at: datetime
    created_by: str = "ai_system"
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    # AI reasoning
    reasoning: str
    affected_sections: List[str] = []
    related_suggestions: List[str] = []


class SuggestionBatch(BaseModel):
    """Batch of related suggestions."""
    id: str
    query: str
    suggestions: List[UpdateSuggestion]
    status: SuggestionStatus = SuggestionStatus.PENDING
    created_at: datetime
    metadata: Dict[str, Any] = {}