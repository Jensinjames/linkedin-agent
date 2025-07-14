"""Module defines the main entry point for the Apify LlamaIndex Agent.

This Agent template is intended to give example on how to use LlamaIndex Agent with Apify Actors.
It extracts contact details from a plain text query with a URL.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from __future__ import annotations

"""Main entry point for the LinkedIn agent."""

from typing import TYPE_CHECKING

from .container import container
from .exceptions import ValidationError as AgentValidationError, CrawlerError, AgentError

if TYPE_CHECKING:
    pass


async def main(adapter):
    """
    Main entry point for the LinkedIn Agent.
    
    Uses dependency injection to orchestrate the entire workflow through
    the processor, which handles routing between agent and crawler modes.
    """
    adapter.log_info('Starting LinkedIn Agent')
    
    try:
        # Get input
        raw_input = await adapter.get_input()
        
        # Process through the orchestrated workflow
        processor = container.get_processor()
        result = await processor.process_request(raw_input)
        
        # Output results
        await adapter.push_data(result)
        
    except (AgentValidationError, CrawlerError, AgentError) as e:
        await adapter.fail(e.message, e.original_error)
    except Exception as e:
        await adapter.fail('Unexpected error occurred', e)

