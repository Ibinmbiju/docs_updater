"""Custom exceptions for the application."""


class DocumentUpdateException(Exception):
    """Base exception for document update operations."""
    pass


class DocumentProcessingError(DocumentUpdateException):
    """Raised when document processing fails."""
    pass


class AIServiceError(DocumentUpdateException):
    """Raised when AI service operations fail."""
    pass


class StorageError(DocumentUpdateException):
    """Raised when storage operations fail."""
    pass


class ValidationError(DocumentUpdateException):
    """Raised when data validation fails."""
    pass