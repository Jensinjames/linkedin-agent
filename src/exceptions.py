"""Custom exception hierarchy for the LinkedIn agent."""


class LinkedInAgentError(Exception):
    """Base exception for all LinkedIn agent errors."""
    
    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class ValidationError(LinkedInAgentError):
    """Raised when input validation fails."""
    pass


class CrawlerError(LinkedInAgentError):
    """Raised when crawling operations fail."""
    pass


class AgentError(LinkedInAgentError):
    """Raised when agent operations fail."""
    pass


class LLMError(LinkedInAgentError):
    """Raised when LLM operations fail."""
    pass


class AdapterError(LinkedInAgentError):
    """Raised when adapter operations fail."""
    pass
