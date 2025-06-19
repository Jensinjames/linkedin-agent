"""Module defines the main entry point for the Apify LlamaIndex Agent.

This Agent template is intended to give example on how to use LlamaIndex Agent with Apify Actors.
It extracts contact details from a plain text query with a URL.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify import Actor
from llama_index.llms.openai import OpenAI
from crawler.linkedin import run_linkedin_crawler  # Your core crawling logic

from .agent import run_agent

if TYPE_CHECKING:
    from llama_index.core.chat_engine.types import AgentChatResponse


async def main(adapter):
    adapter.log_info('Starting LinkedIn Crawler')
    try:
        actor_input = await adapter.get_input()
        # Validate input (add your own validation here)
        if not actor_input or 'query' not in actor_input:
            await adapter.fail('No query provided in input')
            return
        # Run the core crawling logic
        result = await run_linkedin_crawler(actor_input['query'])
        await adapter.push_data(result)
    except Exception as e:
        await adapter.fail('Failed to process query', e)


async def check_inputs(actor_input: dict) -> None:
    """Check that provided input exists.

    :raises Exception: If query is not provided
    """
    if not actor_input.get('query'):
        msg = 'Input `query` is not provided. Please verify that the `query` is correctly set.'
        await Actor.fail(status_message=msg)


async def run_query(query: str, model_name: str) -> AgentChatResponse | None:
    """Process query with LlamaIndex Agent."""
    llm = OpenAI(model=str(model_name), temperature=0)
    try:
        return await run_agent(query=query, llm=llm, verbose=True)
    except Exception as e:
        msg = f'Error running LlamaIndex Agent, error: {e}'
        await Actor.fail(status_message=msg, exception=e)
    return None