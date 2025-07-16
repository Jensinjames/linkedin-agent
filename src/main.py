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
from .exceptions import ValidationError, ServiceError, ProcessingError
from .services.logging_service import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger('main')


async def main(adapter):
    """
    Main entry point for the LinkedIn Agent.
    
    Uses dependency injection to orchestrate the entire workflow through
    the processor, which handles routing between agent and crawler modes.
    """
    logger.info('Starting LinkedIn Agent')
    
    try:
        # Get input
        raw_input = await adapter.get_input()
        logger.debug('Received input', input_size=len(str(raw_input)) if raw_input else 0)
        
        # Process through the orchestrated workflow
        processor = container.get_processor()
        result = await processor.process_request(raw_input)
        
        logger.info('Processing completed successfully', 
                   processing_method=result.get('processing_method', 'unknown'),
                   result_size=len(str(result)))
        
        # Output results
        await adapter.push_data(result)
        
    except (ValidationError, ServiceError, ProcessingError) as e:
        logger.error('Application error occurred', 
                    error_type=type(e).__name__,
                    error_message=e.message)
        await adapter.fail(e.message, e.original_error)
    except Exception as e:
        logger.error('Unexpected error occurred', 
                    error_type=type(e).__name__,
                    error_message=str(e))
        await adapter.fail('Unexpected error occurred', e)

