from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool

from .tools import call_contact_details_scraper, summarize_contact_information
from .exceptions import AgentError

if TYPE_CHECKING:
    from llama_index.core.chat_engine.types import AgentChatResponse
    from llama_index.llms.openai import OpenAI

logger = logging.getLogger('apify')


async def run_agent(query: str, llm: OpenAI, *, verbose: bool = False) -> AgentChatResponse:
    """Run an agent to scrape contact details and process it using LLM and tools.

    The function initializes a ReAct agent with specific tools to process a user-provided query.

    Args:
        query: Query string provided by the user for processing.
        llm: The language model to be used for processing.
        verbose: Flag to enable verbose logging.

    Returns:
        AgentChatResponse: The response from the agent.
        
    Raises:
        AgentError: If the agent operation fails.
    """
    try:
        # Create tools with the LLM instance passed directly
        contact_scraper_tool = FunctionTool.from_defaults(fn=call_contact_details_scraper)
        
        # Create a wrapper for the summarizer that includes the LLM
        async def summarize_with_llm(contact_information: list[dict]) -> str:
            return await summarize_contact_information(contact_information, llm)
        
        summarizer_tool = FunctionTool.from_defaults(fn=summarize_with_llm)

        # Initialize the ReAct Agent with the Tools
        agent = ReActAgent.from_tools(
            [contact_scraper_tool, summarizer_tool],
            llm=llm,
            verbose=verbose,
        )

        response: AgentChatResponse = await agent.achat(query)
        logger.info(f'Agent answer: {response.response}')
        return response
    except Exception as e:
        raise AgentError(f'Failed to execute agent: {str(e)}', e) from e