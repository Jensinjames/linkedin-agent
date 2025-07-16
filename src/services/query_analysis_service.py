"""Query analysis service for determining processing strategy."""

from typing import Dict, Any
from ..config.settings import config
from ..interfaces import AbstractQueryAnalysisService


class QueryAnalysisService(AbstractQueryAnalysisService):
    """Service for analyzing queries and determining processing strategy."""
    
    def __init__(self):
        """Initialize the query analysis service."""
        pass
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query and determine the best processing approach.
        
        Args:
            query: User query to analyze
            
        Returns:
            Dictionary containing analysis results:
            - should_use_agent: bool
            - detected_urls: list[str]
            - query_type: str
            - confidence: float
        """
        query_lower = query.lower()
        urls = self._extract_urls(query)
        action_words = config.agent.action_words
        
        # Determine if query contains action words
        has_action_words = any(word in query_lower for word in action_words)
        
        # Determine query type
        if urls and not has_action_words:
            query_type = "url_extraction"
            should_use_agent = False
            confidence = 0.9
        elif has_action_words:
            query_type = "agent_processing"
            should_use_agent = True
            confidence = 0.8
        else:
            query_type = "general_query"
            should_use_agent = True
            confidence = 0.6
        
        return {
            "should_use_agent": should_use_agent,
            "detected_urls": urls,
            "query_type": query_type,
            "confidence": confidence,
            "has_action_words": has_action_words
        }
    
    def _extract_urls(self, query: str) -> list[str]:
        """Extract URLs from a query string."""
        words = query.split()
        return [word for word in words if word.startswith(('http://', 'https://'))]
