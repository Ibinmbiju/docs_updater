"""Schemas package."""

from .document import (
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentSectionResponse,
    SearchRequest,
    SearchResponse,
)
from .suggestion import (
    DiffHunkResponse,
    GenerateSuggestionsRequest,
    SuggestionBatchResponse,
    SuggestionListResponse,
    SuggestionResponse,
    UpdateSuggestionRequest,
)

__all__ = [
    "DocumentDetailResponse",
    "DocumentListResponse", 
    "DocumentResponse",
    "DocumentSectionResponse",
    "SearchRequest",
    "SearchResponse",
    "DiffHunkResponse",
    "GenerateSuggestionsRequest",
    "SuggestionBatchResponse",
    "SuggestionListResponse",
    "SuggestionResponse", 
    "UpdateSuggestionRequest",
]