"""Abstract base classes for service interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AbstractScraperService(ABC):
    """Abstract interface for scraper services."""
    
    @abstractmethod
    async def scrape_contact_details(
        self,
        start_urls: List[Dict[str, Any]],
        max_requests_per_start_url: int = 5,
        max_depth: int = 2,
        *,
        same_domain: bool = True,
        deduplicate: bool = True,
    ) -> List[Dict]:
        """Scrape contact details from provided URLs."""
        pass


class AbstractSummarizationService(ABC):
    """Abstract interface for summarization services."""
    
    @abstractmethod
    async def summarize_contact_information(self, contact_information: List[Dict]) -> str:
        """Summarize contact information using language model."""
        pass


class AbstractValidationService(ABC):
    """Abstract interface for validation services."""
    
    @abstractmethod
    async def validate_and_parse_input(self, raw_input: Dict[str, Any] | None):
        """Validate and parse raw input into structured format."""
        pass
    
    @abstractmethod
    def should_use_agent_for_query(self, query: str) -> bool:
        """Determine if query requires agent processing."""
        pass


class AbstractQueryAnalysisService(ABC):
    """Abstract interface for query analysis services."""
    
    @abstractmethod
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query and return processing strategy."""
        pass


class AbstractCrawler(ABC):
    """Abstract interface for crawler implementations."""
    
    @abstractmethod
    async def crawl_urls(
        self,
        query: str,
        max_depth: int = 2,
        include_socials: bool = True,
    ) -> Dict[str, Any]:
        """Crawl URLs and extract contact details."""
        pass


class AbstractAgent(ABC):
    """Abstract interface for agent implementations."""
    
    @abstractmethod
    async def process_query(self, query: str, *, verbose: bool = False):
        """Process query using agent with tools."""
        pass
