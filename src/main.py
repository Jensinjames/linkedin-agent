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
from src.crawler.linkedin import run_linkedin_crawler
from src.agent import run_agent
from src.schemas import ActorInput
from pydantic import ValidationError

if TYPE_CHECKING:
    from llama_index.core.chat_engine.types import AgentChatResponse


async def main(adapter):
    """
    Main entry point for the Apify LlamaIndex Agent Actor.
    
    Validates input using the ActorInput schema, runs the LinkedIn crawler with the provided parameters, and pushes the result data. If input validation or processing fails, the actor is marked as failed with an appropriate error message.
    """
    adapter.log_info('Starting LinkedIn Crawler')
    try:
        raw_input = await adapter.get_input()
        try:
            data = ActorInput.model_validate(raw_input or {})
        except ValidationError as e:
            await adapter.fail('Invalid input', e)
            return

        result = await run_linkedin_crawler(
            data.query,
            max_depth=data.maxDepth,
            include_socials=data.includeSocials,
        )

        if getattr(data, "summarizeResults", False):
            llm = OpenAI(model=str(data.modelName), temperature=0)
            summary = await run_agent(
                None,
                llm=llm,
                contact_information=result["results"],
                verbose=True,
            )
            result["summary"] = summary

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


async def run_query(query: str, model_name: str) -> str | None:
    """
    Executes a query using the LlamaIndex Agent with the specified OpenAI model.
    
    Parameters:
        query (str): The input query to process.
        model_name (str): The name of the OpenAI model to use.
    
    Returns:
        str | None: The agent's response if successful; otherwise, None if an error occurs.
    """
    llm = OpenAI(model=str(model_name), temperature=0)
    try:
        return await run_agent(query=query, llm=llm, verbose=True)
    except Exception as e:
        msg = f'Error running LlamaIndex Agent, error: {e}'
        await Actor.fail(status_message=msg, exception=e)
    return None

