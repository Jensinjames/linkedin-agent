"""Core agent functionality for the LinkedIn agent."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool

from ..services.apify.scraper_service import ContactDetailsScraperService
from ..services.llm.summarization_service import SummarizationService
from ..exceptions import AgentError

if TYPE_CHECKING:
    from llama_index.core.chat_engine.types import AgentChatResponse
    from llama_index.llms.openai import OpenAI

logger = logging.getLogger('apify')


class LinkedInAgent:
    """Core agent for processing LinkedIn queries."""
    
    def __init__(self, llm: 'OpenAI', scraper_service: ContactDetailsScraperService, 
                 summarization_service: SummarizationService):
        """
        Initialize the LinkedIn agent with required services.
        
        Args:
            llm: Language model instance
            scraper_service: Service for scraping contact details
            summarization_service: Service for summarizing results
        """
        self.llm = llm
        self.scraper_service = scraper_service
        self.summarization_service = summarization_service
    
    async def process_query(self, query: str, *, verbose: bool = False) -> AgentChatResponse:
        """
        Process a user query using the agent with configured tools.
        
        Args:
            query: User query to process
            verbose: Enable verbose logging
            
        Returns:
            AgentChatResponse: The agent's response
            
        Raises:
            AgentError: If agent processing fails
        """
        try:
            # Create tools with dependency injection
            scraper_tool = FunctionTool.from_defaults(
                fn=self.scraper_service.scrape_contact_details,
                name="contact_details_scraper",
                description="Extract contact details from websites"
            )
            
            summarizer_tool = FunctionTool.from_defaults(
                fn=self.summarization_service.summarize_contact_information,
                name="summarize_contacts",
                description="Summarize scraped contact information"
            )

            # Initialize the ReAct Agent
            agent = ReActAgent.from_tools(
                [scraper_tool, summarizer_tool],
                llm=self.llm,
                verbose=verbose,
            )

            response: AgentChatResponse = await agent.achat(query)
            logger.info(f'Agent answer: {response.response}')
            return response
            
        except Exception as e:
            raise AgentError(f'Failed to execute agent: {str(e)}', e) from e


# Backward compatibility function
async def run_agent(query: str, llm: 'OpenAI', *, verbose: bool = False) -> AgentChatResponse:
    """
    Legacy function for backward compatibility.
    
    This function maintains the existing interface while using the new agent class.
    """
    from ..services.apify.scraper_service import ContactDetailsScraperService
    from ..services.llm.summarization_service import SummarizationService
    
    scraper_service = ContactDetailsScraperService()
    summarization_service = SummarizationService(llm)
    
    agent = LinkedInAgent(llm, scraper_service, summarization_service)
    return await agent.process_query(query, verbose=verbose)
