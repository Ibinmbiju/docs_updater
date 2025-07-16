# Suggestions router
"""FastAPI router for suggestion endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from ..models.suggestion import SuggestionStatus, SuggestionType, UpdateSuggestion
from ..schemas.suggestion import (
    GenerateSuggestionsRequest, 
    SuggestionResponse, 
    SuggestionBatchResponse,
    UpdateSuggestionRequest
)
from ..services.ai_service import AIService
from ..services.document_processor import DocumentProcessor
from ..utils.exceptions import AIServiceError, DocumentProcessingError

router = APIRouter(prefix="/suggestions", tags=["suggestions"])

# In-memory storage for suggestions (in production, use a database)
suggestions_store: dict[str, UpdateSuggestion] = {}


@router.post("/generate", response_model=SuggestionBatchResponse, response_model_exclude_unset=True)
async def generate_suggestions(request: GenerateSuggestionsRequest, fastapi_request: Request) -> SuggestionBatchResponse:
    """Generate update suggestions based on a query."""
    try:
        ai_service = fastapi_request.app.state.ai_service
        doc_processor = fastapi_request.app.state.doc_processor
        print(f"[DEBUG] Generating suggestions for query: {request.query}")
        
        # Limit to 3 with fast embedding search
        max_suggestions = 3
        
        # Search for relevant sections (limit to 3 for speed)
        relevant_sections = await doc_processor.search_sections(
            query=request.query,
            limit=max_suggestions
        )
        
        print(f"[DEBUG] Found {len(relevant_sections)} relevant sections")
        
        if not relevant_sections:
            print("[DEBUG] No relevant sections found, returning empty response")
            return SuggestionBatchResponse(
                query=request.query,
                suggestions=[],
                total_suggestions=0,
                message="No relevant sections found for the query"
            )
        
        # Generate suggestions using AI service (only for top 3 sections)
        print(f"[DEBUG] Starting AI suggestion generation for {len(relevant_sections)} sections")
        try:
            suggestions = await ai_service.generate_suggestions(
                query=request.query,
                relevant_sections=relevant_sections
            )
            print(f"[DEBUG] AI service returned {len(suggestions)} suggestions")
        except Exception as e:
            print(f"[ERROR] AI service failed during suggestion generation: {str(e)}")
            raise
        
        # Only keep the first 3 suggestions for speed
        suggestions = suggestions[:max_suggestions]
        
        print(f"[DEBUG] Generated {len(suggestions)} suggestions")
        
        # Store suggestions in memory
        for suggestion in suggestions:
            suggestions_store[suggestion.id] = suggestion
        
        print(f"[DEBUG] Stored {len(suggestions)} suggestions in memory store")
        
        # Convert to response format
        suggestion_responses = [
            SuggestionResponse(
                id=suggestion.id,
                document_id=suggestion.document_id,
                section_id=suggestion.section_id,
                title=suggestion.title,
                description=suggestion.description,
                suggestion_type=suggestion.suggestion_type,
                status=suggestion.status,
                confidence_score=suggestion.confidence_score,
                created_at=suggestion.created_at,
                updated_at=suggestion.updated_at,
                reasoning=suggestion.reasoning,
                diff_hunks=suggestion.diff_hunks,
                original_content=suggestion.original_content,
                suggested_content=suggestion.suggested_content
            ) for suggestion in suggestions
        ]
        
        response = SuggestionBatchResponse(
            query=request.query,
            suggestions=suggestion_responses,
            total_suggestions=len(suggestion_responses),
            message=f"Generated {len(suggestion_responses)} suggestions"
        )
        
        print(f"[DEBUG] Returning response with {len(suggestion_responses)} suggestions")
        return response
        
    except AIServiceError as e:
        print(f"[ERROR] AI Service error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e),
                "hint": "Check your OpenAI API key in the .env file or environment variables. Suggestions cannot be generated without it."
            }
        )
    except DocumentProcessingError as e:
        print(f"[ERROR] Document processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/")
async def list_suggestions(
    status: Optional[SuggestionStatus] = Query(None, description="Filter by status"),
    suggestion_type: Optional[SuggestionType] = Query(None, description="Filter by type"),
    limit: int = Query(20, ge=1, le=100, description="Number of suggestions to return")
) -> List[SuggestionResponse]:
    """List all suggestions with optional filtering."""
    try:
        suggestions = list(suggestions_store.values())
        print(f"[DEBUG] Total suggestions in store: {len(suggestions)}")
        
        # Apply filters
        if status:
            suggestions = [s for s in suggestions if s.status == status]
            print(f"[DEBUG] After status filter ({status}): {len(suggestions)} suggestions")
        if suggestion_type:
            suggestions = [s for s in suggestions if s.suggestion_type == suggestion_type]
            print(f"[DEBUG] After type filter ({suggestion_type}): {len(suggestions)} suggestions")
        
        # Apply limit
        suggestions = suggestions[:limit]
        print(f"[DEBUG] After limit ({limit}): {len(suggestions)} suggestions")
        
        response_suggestions = [
            SuggestionResponse(
                id=suggestion.id,
                document_id=suggestion.document_id,
                section_id=suggestion.section_id,
                title=suggestion.title,
                description=suggestion.description,
                suggestion_type=suggestion.suggestion_type,
                status=suggestion.status,
                confidence_score=suggestion.confidence_score,
                created_at=suggestion.created_at,
                updated_at=suggestion.updated_at,
                reasoning=suggestion.reasoning,
                diff_hunks=suggestion.diff_hunks,
                original_content=suggestion.original_content,
                suggested_content=suggestion.suggested_content
            ) for suggestion in suggestions
        ]
        
        print(f"[DEBUG] Returning {len(response_suggestions)} suggestions")
        return response_suggestions
        
    except Exception as e:
        print(f"[ERROR] Error in list_suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{suggestion_id}")
async def get_suggestion(suggestion_id: str) -> SuggestionResponse:
    """Get a specific suggestion by ID."""
    try:
        suggestion = suggestions_store.get(suggestion_id)
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        return SuggestionResponse(
            id=suggestion.id,
            document_id=suggestion.document_id,
            section_id=suggestion.section_id,
            title=suggestion.title,
            description=suggestion.description,
            suggestion_type=suggestion.suggestion_type,
            status=suggestion.status,
            confidence_score=suggestion.confidence_score,
            created_at=suggestion.created_at,
            updated_at=suggestion.updated_at,
            reasoning=suggestion.reasoning,
            diff_hunks=suggestion.diff_hunks,
            original_content=suggestion.original_content,
            suggested_content=suggestion.suggested_content
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{suggestion_id}")
async def update_suggestion(
    suggestion_id: str, 
    request: UpdateSuggestionRequest
) -> SuggestionResponse:
    """Update a suggestion (approve, reject, etc.)."""
    try:
        suggestion = suggestions_store.get(suggestion_id)
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        # Update suggestion
        from datetime import datetime
        
        if request.status is not None:
            suggestion.status = request.status
        if request.reviewed_by is not None:
            suggestion.reviewed_by = request.reviewed_by
            suggestion.reviewed_at = datetime.now()
        
        suggestion.updated_at = datetime.now()
        
        # Store updated suggestion
        suggestions_store[suggestion_id] = suggestion
        
        return SuggestionResponse(
            id=suggestion.id,
            document_id=suggestion.document_id,
            section_id=suggestion.section_id,
            title=suggestion.title,
            description=suggestion.description,
            suggestion_type=suggestion.suggestion_type,
            status=suggestion.status,
            confidence_score=suggestion.confidence_score,
            created_at=suggestion.created_at,
            updated_at=suggestion.updated_at,
            reasoning=suggestion.reasoning,
            diff_hunks=suggestion.diff_hunks,
            original_content=suggestion.original_content,
            suggested_content=suggestion.suggested_content
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{suggestion_id}")
async def delete_suggestion(suggestion_id: str) -> JSONResponse:
    """Delete a suggestion."""
    try:
        if suggestion_id not in suggestions_store:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        del suggestions_store[suggestion_id]
        
        return JSONResponse({
            "message": "Suggestion deleted successfully",
            "suggestion_id": suggestion_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{suggestion_id}/approve")
async def approve_suggestion(suggestion_id: str) -> JSONResponse:
    """Approve a suggestion."""
    try:
        suggestion = suggestions_store.get(suggestion_id)
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        from datetime import datetime
        
        suggestion.status = SuggestionStatus.APPROVED
        suggestion.updated_at = datetime.now()
        suggestions_store[suggestion_id] = suggestion
        
        return JSONResponse({
            "message": "Suggestion approved successfully",
            "suggestion_id": suggestion_id,
            "status": suggestion.status
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{suggestion_id}/reject")
async def reject_suggestion(suggestion_id: str) -> JSONResponse:
    """Reject a suggestion."""
    try:
        suggestion = suggestions_store.get(suggestion_id)
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        from datetime import datetime
        
        suggestion.status = SuggestionStatus.REJECTED
        suggestion.updated_at = datetime.now()
        suggestions_store[suggestion_id] = suggestion
        
        return JSONResponse({
            "message": "Suggestion rejected",
            "suggestion_id": suggestion_id,
            "status": suggestion.status
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{suggestion_id}/diff")
async def get_suggestion_diff(suggestion_id: str) -> JSONResponse:
    """Get the diff for a specific suggestion."""
    try:
        suggestion = suggestions_store.get(suggestion_id)
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        from ..services.diff_service import DiffService
        
        # Get diff statistics
        diff_stats = DiffService.get_diff_stats(suggestion.diff_hunks)
        
        return JSONResponse({
            "suggestion_id": suggestion_id,
            "diff_hunks": [hunk.model_dump() for hunk in suggestion.diff_hunks],
            "stats": diff_stats,
            "original_content": suggestion.original_content,
            "suggested_content": suggestion.suggested_content
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/stats/overview")
async def get_suggestions_stats() -> JSONResponse:
    """Get overview statistics for all suggestions."""
    try:
        suggestions = list(suggestions_store.values())
        
        stats = {
            "total_suggestions": len(suggestions),
            "by_status": {},
            "by_type": {},
            "average_confidence": 0.0
        }
        
        for status in SuggestionStatus:
            stats["by_status"][status.value] = len([s for s in suggestions if s.status == status])
        
        for suggestion_type in SuggestionType:
            stats["by_type"][suggestion_type.value] = len([s for s in suggestions if s.suggestion_type == suggestion_type])
        
        if suggestions:
            stats["average_confidence"] = sum(s.confidence_score for s in suggestions) / len(suggestions)
        
        return JSONResponse(stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
