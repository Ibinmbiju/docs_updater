"""Suggestion schemas for API responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..models.suggestion import (
    DiffHunk,
    SuggestionBatch,
    SuggestionStatus,
    SuggestionType,
    UpdateSuggestion,
)
from ..services.diff_service import DiffService


class GenerateSuggestionsRequest(BaseModel):
    """Generate suggestions request schema."""
    query: str
    limit: int = 10
    context: Optional[str] = None
    target_sections: Optional[List[str]] = None


class UpdateSuggestionRequest(BaseModel):
    """Update suggestion request schema."""
    status: Optional[SuggestionStatus] = None
    reviewed_by: Optional[str] = None


class DiffHunkResponse(BaseModel):
    """Diff hunk response schema."""
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    old_lines: List[str]
    new_lines: List[str]
    context_before: List[str] = []
    context_after: List[str] = []


class SuggestionResponse(BaseModel):
    """Suggestion response schema."""
    id: str
    document_id: str
    section_id: str
    title: str
    description: str
    suggestion_type: SuggestionType
    status: SuggestionStatus
    confidence_score: float
    
    # Diff information
    diff_hunks: List[DiffHunk]
    original_content: str
    suggested_content: str
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: str = "ai_system"
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    # AI reasoning
    reasoning: str
    affected_sections: List[str] = []
    
    @classmethod
    def from_suggestion(cls, suggestion: UpdateSuggestion) -> "SuggestionResponse":
        """Create response from suggestion model."""
        return cls(
            id=suggestion.id,
            document_id=suggestion.document_id,
            section_id=suggestion.section_id,
            title=suggestion.title,
            description=suggestion.description,
            suggestion_type=suggestion.suggestion_type,
            status=suggestion.status,
            confidence_score=suggestion.confidence_score,
            diff_hunks=suggestion.diff_hunks,
            original_content=suggestion.original_content,
            suggested_content=suggestion.suggested_content,
            created_at=suggestion.created_at,
            updated_at=suggestion.updated_at,
            created_by=suggestion.created_by,
            reviewed_by=suggestion.reviewed_by,
            reviewed_at=suggestion.reviewed_at,
            reasoning=suggestion.reasoning,
            affected_sections=suggestion.affected_sections
        )


class SuggestionUpdateRequest(BaseModel):
    """Suggestion update request schema."""
    status: Optional[SuggestionStatus] = None
    suggested_content: Optional[str] = None
    description: Optional[str] = None
    reviewed_by: Optional[str] = None


class SuggestionBatchResponse(BaseModel):
    """Suggestion batch response schema."""
    query: str
    suggestions: List[SuggestionResponse]
    total_suggestions: int
    message: Optional[str] = None
    
    @classmethod
    def from_batch(cls, batch: SuggestionBatch) -> "SuggestionBatchResponse":
        """Create response from batch model."""
        suggestions = [SuggestionResponse.from_suggestion(s) for s in batch.suggestions]
        
        return cls(
            query=batch.query,
            suggestions=suggestions,
            total_suggestions=len(batch.suggestions),
            message=f"Generated {len(batch.suggestions)} suggestions"
        )


class SuggestionListResponse(BaseModel):
    """Suggestion list response schema."""
    suggestions: List[SuggestionResponse]
    total: int
    filter_status: Optional[SuggestionStatus] = None