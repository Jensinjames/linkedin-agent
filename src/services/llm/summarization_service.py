"""LLM summarization service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llama_index.core.prompts import PromptTemplate

from ...exceptions import LLMError

if TYPE_CHECKING:
    from llama_index.llms.openai import OpenAI

logger = logging.getLogger('apify')


class SummarizationService:
    """Service for summarizing contact information using LLM."""
    
    PROMPT_SUMMARIZE = PromptTemplate(
        'Scraped contact data is below.\n'
        '---------------------\n'
        '{scraped_data}\n'
        '---------------------\n'
        'Given the scraped contact information and no prior knowledge, '
        'summarize contact information in a concise and informative manner.\n'
        'Summary of contact details:'
    )
    
    def __init__(self, llm: 'OpenAI'):
        """
        Initialize the summarization service.
        
        Args:
            llm: Language model instance to use for summarization
        """
        self.llm = llm
    
    async def summarize_contact_information(self, contact_information: list[dict]) -> str:
        """
        Summarize list of scraped contacts.

        Args:
            contact_information: List of contact information to summarize

        Returns:
            Summarized contact information as string

        Raises:
            LLMError: If the summarization operation fails
        """
        try:
            logger.info('Summarizing contact information')
            return str(await self.llm.apredict(
                self.PROMPT_SUMMARIZE, 
                scraped_data=contact_information
            ))
        except Exception as e:
            raise LLMError(f'Failed to summarize contact information: {str(e)}', e) from e


# Backward compatibility function
async def summarize_contact_information(contact_information: list[dict], llm: 'OpenAI') -> str:
    """
    Legacy function for backward compatibility.
    
    This function maintains the existing interface while using the new service class.
    """
    service = SummarizationService(llm)
    return await service.summarize_contact_information(contact_information)
