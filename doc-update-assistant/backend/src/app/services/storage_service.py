# Storage service
"""Storage service for documents and suggestions."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from ..models.document import Document, DocumentSection
from ..models.suggestion import UpdateSuggestion
from ..utils.exceptions import StorageError


class StorageService:
    """Handles storage operations for documents and suggestions."""
    
    def __init__(self, storage_path: str = "data") -> None:
        """Initialize the storage service."""
        self.storage_path = Path(storage_path)
        self.documents_path = self.storage_path / "documents"
        self.suggestions_path = self.storage_path / "suggestions"
        
        # Create directories if they don't exist
        self.documents_path.mkdir(parents=True, exist_ok=True)
        self.suggestions_path.mkdir(parents=True, exist_ok=True)
    
    async def save_document(self, document: Document) -> bool:
        """Save a document to storage."""
        return await self._save_json_file(
            self.documents_path / f"{document.id}.json",
            document.model_dump()
        )
    
    async def load_document(self, document_id: str) -> Optional[Document]:
        """Load a document from storage."""
        data = await self._load_json_file(self.documents_path / f"{document_id}.json")
        return Document(**data) if data else None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from storage."""
        return await self._delete_file(self.documents_path / f"{document_id}.json")
    
    async def list_documents(self) -> List[str]:
        """List all stored document IDs."""
        return await self._list_json_files(self.documents_path)
    
    async def save_suggestion(self, suggestion: UpdateSuggestion) -> bool:
        """Save a suggestion to storage."""
        return await self._save_json_file(
            self.suggestions_path / f"{suggestion.id}.json",
            suggestion.model_dump()
        )
    
    async def load_suggestion(self, suggestion_id: str) -> Optional[UpdateSuggestion]:
        """Load a suggestion from storage."""
        data = await self._load_json_file(self.suggestions_path / f"{suggestion_id}.json")
        return UpdateSuggestion(**data) if data else None
    
    async def delete_suggestion(self, suggestion_id: str) -> bool:
        """Delete a suggestion from storage."""
        return await self._delete_file(self.suggestions_path / f"{suggestion_id}.json")
    
    async def list_suggestions(self) -> List[str]:
        """List all stored suggestion IDs."""
        return await self._list_json_files(self.suggestions_path)
    
    async def get_storage_stats(self) -> Dict[str, int]:
        """Get storage statistics."""
        return {
            "total_documents": len(list(self.documents_path.glob("*.json"))),
            "total_suggestions": len(list(self.suggestions_path.glob("*.json"))),
            "storage_size_bytes": self._get_directory_size(self.storage_path)
        }
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of a directory in bytes."""
        total_size = 0
        
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size

    async def _save_json_file(self, file_path: Path, data: Dict) -> bool:
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            raise StorageError(f"Failed to save file {file_path}: {str(e)}")

    async def _load_json_file(self, file_path: Path) -> Optional[Dict]:
        """Load data from JSON file."""
        try:
            if not file_path.exists():
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to load file {file_path}: {str(e)}")

    async def _delete_file(self, file_path: Path) -> bool:
        """Delete a file."""
        try:
            if file_path.exists():
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            raise StorageError(f"Failed to delete file {file_path}: {str(e)}")

    async def _list_json_files(self, directory: Path) -> List[str]:
        """List all JSON file stems in directory."""
        try:
            return [file_path.stem for file_path in directory.glob("*.json")]
        except Exception as e:
            raise StorageError(f"Failed to list files in {directory}: {str(e)}")
