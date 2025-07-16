"""Core processor for orchestrating LinkedIn agent workflows."""

from typing import Any, Dict

from ..services.validation_service import InputValidationService
from ..services.query_analysis_service import QueryAnalysisService
from ..models.schemas import ActorInput
from ..exceptions import ServiceError, ProcessingError
from ..services.logging_service import get_logger

logger = get_logger('processor')


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
        self.query_analysis_service = QueryAnalysisService()
    
    async def process_request(self, raw_input: Dict[str, Any] | None) -> Dict[str, Any]:
        """
        Process a complete request from raw input to final output.
        
        Args:
            raw_input: Raw input dictionary
            
        Returns:
            Processed results dictionary with analysis metadata
            
        Raises:
            ValidationError: If input validation fails
            ServiceError: If external services fail
            ProcessingError: If internal processing fails
        """
        logger.info('Starting request processing')
        
        # Validate input
        data = await self.validation_service.validate_and_parse_input(raw_input)
        logger.debug('Input validation successful', query_length=len(data.query))
        
        # Analyze query to determine processing method
        analysis = self.query_analysis_service.analyze_query(data.query)
        logger.info('Query analysis completed', 
                   query_type=analysis['query_type'],
                   should_use_agent=analysis['should_use_agent'],
                   confidence=analysis['confidence'])
        
        if analysis["should_use_agent"]:
            result = await self._process_with_agent(data)
        else:
            result = await self._process_with_crawler(data)
        
        # Add analysis metadata to result
        result["query_analysis"] = analysis
        logger.info('Request processing completed', 
                   processing_method=result.get('processing_method'))
        return result
    
    async def _process_with_agent(self, data: ActorInput) -> Dict[str, Any]:
        """Process using the agent for complex queries."""
        try:
            logger.info('Processing with agent', query=data.query)
            response = await self.agent.process_query(data.query, verbose=True)
            logger.info('Agent processing completed')
            return {
                "query": data.query,
                "agent_response": str(response.response),
                "processing_method": "agent"
            }
        except Exception as e:
            logger.error('Agent processing failed', error_message=str(e))
            raise ProcessingError('Failed to process query with agent', e) from e
    
    async def _process_with_crawler(self, data: ActorInput) -> Dict[str, Any]:
        """Process using the crawler for simple URL extraction."""
        try:
            logger.info('Processing with crawler', 
                       query=data.query,
                       max_depth=data.maxDepth,
                       include_socials=data.includeSocials)
            result = await self.crawler.crawl_urls(
                data.query,
                max_depth=data.maxDepth,
                include_socials=data.includeSocials,
            )
            result["processing_method"] = "crawler"
            logger.info('Crawler processing completed', 
                       result_count=len(result.get('results', [])))
            return result
        except Exception as e:
            logger.error('Crawler processing failed', error_message=str(e))
            raise ServiceError('Failed to crawl LinkedIn URLs', e) from e
