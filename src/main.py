"""Module defines the main entry point for the LinkedIn Agent.

This module provides the main entry point for the LinkedIn agent, which uses
dependency injection to orchestrate the entire workflow through the processor,
handling routing between agent and crawler modes.

For Apify Actor integration, utilize the Apify SDK toolkit.
Read more at: https://docs.apify.com/sdk/python
"""

from __future__ import annotations
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

