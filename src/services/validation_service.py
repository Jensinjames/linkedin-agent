"""Input validation service for the LinkedIn agent."""

from typing import Any, Dict
from ..schemas import ActorInput
from ..exceptions import ValidationError as AgentValidationError
from pydantic import ValidationError


class InputValidationService:
    """Service for validating and processing input data."""
    
    @staticmethod
    async def validate_and_parse_input(raw_input: Dict[str, Any] | None) -> ActorInput:
        """
        Validate and parse raw input into ActorInput schema.
        
        Args:
            raw_input: Raw input dictionary to validate
            
        Returns:
            ActorInput: Validated input data
            
        Raises:
            AgentValidationError: If validation fails
        """
        try:
            return ActorInput.model_validate(raw_input or {})
        except ValidationError as e:
            raise AgentValidationError('Invalid input schema', e) from e
    
    @staticmethod
    def should_use_agent_for_query(query: str) -> bool:
        """
        Determine if the query requires agent processing or simple crawling.
        
        Returns True if the query contains action words that suggest the need
        for agent-based processing, False for simple URL extraction.
        """
        action_words = ['summarize', 'analyze', 'find', 'extract', 'process', 'search']
        query_lower = query.lower()
        
        # If query is just URLs, use direct crawler
        # Split and filter out empty strings
        words = [word for word in query.split() if word]
        if words and all(word.startswith(('http://', 'https://')) for word in words):
            return False
        
        # If query contains action words, use agent
        return any(word in query_lower for word in action_words)
