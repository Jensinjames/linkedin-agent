"""Legacy LinkedIn crawler module for backward compatibility."""

# Import the new implementation for backward compatibility
from ..core.crawler import run_linkedin_crawler

__all__ = ['run_linkedin_crawler']

