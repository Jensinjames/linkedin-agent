"""Dependency injection container for the LinkedIn agent."""

from llama_index.llms.openai import OpenAI

from .config.settings import config
from .services.apify.scraper_service import ContactDetailsScraperService
from .services.llm.summarization_service import SummarizationService
from .services.validation_service import InputValidationService
from .services.query_analysis_service import QueryAnalysisService
from .services.logging_service import get_logger
from .core.crawler import LinkedInCrawler
from .core.agent import LinkedInAgent
from .core.processor import LinkedInProcessor

logger = get_logger('container')


class DIContainer:
    """Dependency injection container for managing service instances."""
    
    def __init__(self):
        """Initialize the container with None values for lazy loading."""
        self._scraper_service = None
        self._llm = None
        self._llm_model = None  # Track current model
        self._summarization_service = None
        self._validation_service = None
        self._query_analysis_service = None
        self._crawler = None
        self._agent = None
        self._agent_model = None  # Track agent model
        self._processor = None
    
    def reset(self):
        """Reset all cached instances. Useful for testing or configuration changes."""
        self._scraper_service = None
        self._llm = None
        self._llm_model = None
        self._summarization_service = None
        self._validation_service = None
        self._query_analysis_service = None
        self._crawler = None
        self._agent = None
        self._agent_model = None
        self._processor = None
    
    def get_scraper_service(self) -> ContactDetailsScraperService:
        """Get or create the scraper service instance."""
        if self._scraper_service is None:
            logger.debug('Creating scraper service instance')
            self._scraper_service = ContactDetailsScraperService(config.apify.token)
        return self._scraper_service
    
    def get_llm(self, model_name: str | None = None) -> OpenAI:
        """Get or create the LLM instance."""
        model = model_name or config.llm.default_model
        if self._llm is None or self._llm_model != model:
            logger.debug('Creating LLM instance', model=model)
            self._llm = OpenAI(
                model=model,
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens
            )
            self._llm_model = model
        return self._llm
    
    def get_summarization_service(self, model_name: str | None = None) -> SummarizationService:
        """Get or create the summarization service instance."""
        llm = self.get_llm(model_name)
        if self._summarization_service is None or self._summarization_service.llm != llm:
            self._summarization_service = SummarizationService(llm)
        return self._summarization_service
    
    def get_validation_service(self) -> InputValidationService:
        """Get or create the validation service instance."""
        if self._validation_service is None:
            self._validation_service = InputValidationService()
        return self._validation_service
    
    def get_query_analysis_service(self) -> QueryAnalysisService:
        """Get or create the query analysis service instance."""
        if self._query_analysis_service is None:
            self._query_analysis_service = QueryAnalysisService()
        return self._query_analysis_service
    
    def get_crawler(self) -> LinkedInCrawler:
        """Get or create the crawler instance."""
        if self._crawler is None:
            self._crawler = LinkedInCrawler(self.get_scraper_service())
        return self._crawler
    
    def get_agent(self, model_name: str | None = None) -> LinkedInAgent:
        """Get or create the agent instance."""
        model = model_name or config.llm.default_model
        if self._agent is None or self._agent_model != model:
            llm = self.get_llm(model_name)
            self._agent = LinkedInAgent(
                llm,
                self.get_scraper_service(),
                self.get_summarization_service(model_name)
            )
            self._agent_model = model
        return self._agent
    
    def get_processor(self, model_name: str | None = None) -> LinkedInProcessor:
        """Get or create the processor instance."""
        if self._processor is None:
            self._processor = LinkedInProcessor(
                self.get_crawler(),
                self.get_agent(model_name)
            )
        return self._processor


# Global container instance
container = DIContainer()
