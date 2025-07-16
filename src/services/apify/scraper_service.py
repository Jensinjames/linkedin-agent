"""Apify contact details scraper service."""

from __future__ import annotations

import os
from typing import Any

import polars as pl
from apify_client import ApifyClientAsync

from ...config.settings import config
from ...exceptions import ServiceError
from ...interfaces.base import AbstractScraperService
from ...utils.logging_service import logging_service

logger = logging_service


class ContactDetailsScraperService(AbstractScraperService):
    """Service for scraping contact details using Apify actors."""
    
    def __init__(self, apify_token: str | None = None):
        """
        Initialize the scraper service.
        
        Args:
            apify_token: Apify API token. If None, uses APIFY_TOKEN environment variable.
        """
        token = apify_token or os.getenv('APIFY_TOKEN')
        self.client = ApifyClientAsync(token=token)
    
    async def scrape_contact_details(
        self,
        start_urls: list[dict[str, Any]],
        max_requests_per_start_url: int = 5,
        max_depth: int = 2,
        *,
        same_domain: bool = True,
        deduplicate: bool = True,
    ) -> list[dict]:
        """
        Extract contact details from websites using the Apify Actor.

        Args:
            start_urls: List of dictionaries containing URLs to scrape
            max_requests_per_start_url: Maximum pages to enqueue per start URL
            max_depth: Maximum link depth
            same_domain: Only follow links within the same domain
            deduplicate: Whether to deduplicate results

        Returns:
            List of extracted contact details

        Raises:
            ServiceError: If the scraping operation fails
        """
        run_input = {
            'startUrls': start_urls,
            'maxRequestsPerStartUrl': max_requests_per_start_url,
            'maxDepth': max_depth,
            'sameDomain': same_domain,
        }
        
        try:
            logger.info('Calling Apify Actor', 
                       actor_id=config.apify.contact_details_actor_id,
                       input_data=run_input)
            actor_call = await self.client.actor(config.apify.contact_details_actor_id).call(run_input=run_input)
            dataset_items = await self.client.dataset(actor_call['defaultDatasetId']).list_items(clean=True)  # type: ignore[index]
            data = dataset_items.items
            logger.info('Received data from Apify Actor', 
                       actor_id=config.apify.contact_details_actor_id,
                       record_count=len(data))

            if deduplicate:
                data = self._deduplicate_results(data)

            return data
        except Exception as e:
            raise ServiceError(f'Failed to scrape contact details: {str(e)}', e) from e
    
    def _deduplicate_results(self, data: list[dict]) -> list[dict]:
        """
        Deduplicate contact information results.
        
        Args:
            data: List of contact information records
            
        Returns:
            Deduplicated list of records
        """
        logger.info('Deduplicating contact information')
        df_data = pl.from_records(data)
        columns = list(set(df_data.columns) - config.apify.contact_details_actor_fields)
        return df_data.unique(subset=columns).to_dicts()


# Backward compatibility function
async def call_contact_details_scraper(
    start_urls: list[dict[str, Any]],
    max_requests_per_start_url: int = 5,
    max_depth: int = 2,
    *,
    same_domain: bool = True,
    deduplicate: bool = True,
) -> list[dict]:
    """
    Legacy function for backward compatibility.
    
    This function maintains the existing interface while using the new service class.
    """
    service = ContactDetailsScraperService()
    return await service.scrape_contact_details(
        start_urls, max_requests_per_start_url, max_depth,
        same_domain=same_domain, deduplicate=deduplicate
    )
