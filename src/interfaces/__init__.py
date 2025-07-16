"""Abstract base classes for service interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AbstractScraperService(ABC):
    """Abstract base class for scraper services."""
    
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
        """Extract contact details from websites."""
        pass


class AbstractSummarizationService(ABC):
    """Abstract base class for summarization services."""
    
    @abstractmethod
    async def summarize_contact_information(self, contact_information: List[Dict]) -> str:
        """Summarize list of scraped contacts."""
        pass


class AbstractValidationService(ABC):
    """Abstract base class for validation services."""
    
    @abstractmethod
    async def validate_and_parse_input(self, raw_input: Dict[str, Any] | None):
        """Validate and parse raw input."""
        pass


class AbstractQueryAnalysisService(ABC):
    """Abstract base class for query analysis services."""
    
    @abstractmethod
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze a query and determine processing strategy."""
        pass


class AbstractCrawler(ABC):
    """Abstract base class for crawlers."""
    
    @abstractmethod
    async def crawl_urls(
        self,
        query: str,
        max_depth: int = 2,
        include_socials: bool = True,
    ) -> Dict[str, Any]:
        """Extract contact details from URLs in the query."""
        pass


class AbstractAgent(ABC):
    """Abstract base class for agents."""
    
    @abstractmethod
    async def process_query(self, query: str, *, verbose: bool = False):
        """Process a user query using the agent."""
        pass
