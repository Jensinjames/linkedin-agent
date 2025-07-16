"""Custom exception hierarchy for the LinkedIn agent."""


class LinkedInAgentError(Exception):
    """Base exception for all LinkedIn agent errors."""
    
    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class ValidationError(LinkedInAgentError):
    """Raised when input validation or configuration errors occur."""
    pass


class ServiceError(LinkedInAgentError):
    """Raised when external service operations fail (Apify, LLM, etc)."""
    pass


class ProcessingError(LinkedInAgentError):
    """Raised when internal processing logic fails."""
    pass
