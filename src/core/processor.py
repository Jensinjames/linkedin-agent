"""Core processor for orchestrating LinkedIn agent workflows."""

from typing import Any, Dict

from ..services.validation_service import InputValidationService
from ..schemas import ActorInput
from ..exceptions import CrawlerError, AgentError


class LinkedInProcessor:
    """Central processor for orchestrating LinkedIn data extraction workflows."""
    
    def __init__(self, crawler, agent):
        """
        Initialize the processor with crawler and agent instances.
        
        Args:
            crawler: LinkedIn crawler instance
            agent: LinkedIn agent instance
        """
        self.crawler = crawler
        self.agent = agent
        self.validation_service = InputValidationService()
    
    async def process_request(self, raw_input: Dict[str, Any] | None) -> Dict[str, Any]:
        """
        Process a complete request from raw input to final output.
        
        Args:
            raw_input: Raw input dictionary
            
        Returns:
            Processed results dictionary
            
        Raises:
            ValidationError: If input validation fails
            CrawlerError: If crawling fails
            AgentError: If agent processing fails
        """
        # Validate input
        data = await self.validation_service.validate_and_parse_input(raw_input)
        
        # Determine processing method
        should_use_agent = self.validation_service.should_use_agent_for_query(data.query)
        
        if should_use_agent:
            return await self._process_with_agent(data)
        else:
            return await self._process_with_crawler(data)
    
    async def _process_with_agent(self, data: ActorInput) -> Dict[str, Any]:
        """Process using the agent for complex queries."""
        try:
            response = await self.agent.process_query(data.query, verbose=True)
            return {
                "query": data.query,
                "agent_response": str(response.response),
                "processing_method": "agent"
            }
        except Exception as e:
            raise AgentError('Failed to process query with agent', e) from e
    
    async def _process_with_crawler(self, data: ActorInput) -> Dict[str, Any]:
        """Process using the crawler for simple URL extraction."""
        try:
            result = await self.crawler.crawl_urls(
                data.query,
                max_depth=data.maxDepth,
                include_socials=data.includeSocials,
            )
            result["processing_method"] = "crawler"
            return result
        except Exception as e:
            raise CrawlerError('Failed to crawl LinkedIn URLs', e) from e
