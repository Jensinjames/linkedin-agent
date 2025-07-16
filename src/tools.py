"""Tool functions for backward compatibility."""

# Re-export for backward compatibility
from .services.apify.scraper_service import call_contact_details_scraper
from .services.llm.summarization_service import summarize_contact_information

__all__ = ['call_contact_details_scraper', 'summarize_contact_information']