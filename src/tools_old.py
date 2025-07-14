"""Legacy tools module for backward compatibility."""

# Import the new implementations for backward compatibility
from .services.apify.scraper_service import call_contact_details_scraper
from .services.llm.summarization_service import summarize_contact_information

__all__ = ['call_contact_details_scraper', 'summarize_contact_information']


async def call_contact_details_scraper(
    start_urls: list[dict[str, Any]],
    max_requests_per_start_url: int = 5,
    max_depth: int = 2,
    *,
    same_domain: bool = True,
    deduplicate: bool = True,
) -> list[dict]:
    """Extract contact details from websites using the Apify Actor.

    The Apify Contact Details Scraper is a tool for extracting and downloading various contact information,
    including emails, phone numbers, and social media profiles from websites. This function invokes the
    Apify Actor to process the provided list of URLs.

    The scraper retrieves contact details for every URL it encounters, with crawling behavior controlled by
    the max_depth and max_requests_per_start_url parameters.

    Since the scraper often produces a list of URLs with duplicate contact details, it is recommended to
    deduplicate the results.

    Args:
        start_urls: List of dictionaries containing the URLs to be scraped, for example: "startUrls": [{"url": "https://apify.com"}]
        max_requests_per_start_url: The maximum number of pages that will be enqueued from each start URL you provide.
        max_depth: Maximum link depth
        same_domain: If set, the scraper will only follow links within the same domain as the referring page.
        deduplicate: If set, this function will deduplicate the results.

    Returns:
        List of extracted details

        Sample output:
        [
            {
               "url": "https://apify.com/",
               "domain": "apify.com",
               "linkedIns": [ "https://www.linkedin.com/company/apifytech/" ],
               "twitters": [ "https://x.com/apify" ],
            },
            {
               "url": "https://apify.com/jobs",
               "domain": "apify.com",
            }
        ]
        
    Raises:
        CrawlerError: If the scraping operation fails.
    """
    run_input = {
        'startUrls': start_urls,
        'maxRequestsPerStartUrl': max_requests_per_start_url,
        'maxDepth': max_depth,
        'sameDomain': same_domain,
    }
    
    try:
        logger.info(f'Calling Apify Actor: {CONTACT_DETAILS_ACTOR_ID} with input: {run_input}')
        actor_call = await client.actor(CONTACT_DETAILS_ACTOR_ID).call(run_input=run_input)
        dataset_items = await client.dataset(actor_call['defaultDatasetId']).list_items(clean=True)  # type: ignore[index]
        data = dataset_items.items
        logger.info('Received data from %s, number of records: %d', CONTACT_DETAILS_ACTOR_ID, len(data))

        if deduplicate:
            logger.info('Deduplicating contact information')
            df_data = pl.from_records(data)
            columns = list(set(df_data.columns) - CONTACT_DETAILS_ACTOR_FIELDS)
            data = df_data.unique(subset=columns).to_dicts()

        return data
    except Exception as e:
        raise CrawlerError(f'Failed to scrape contact details: {str(e)}', e) from e


async def summarize_contact_information(contact_information: list[dict], llm: 'OpenAI') -> str:
    """Summarize list of scraped contacts from the Contact Details Scraper.

    Args:
        contact_information (list[dict]): List of contact information obtained from the Contact Details Scraper.
        llm: The language model instance to use for summarization.
        Sample input:
        [
            {
               "url": "https://apify.com/",
               "domain": "apify.com",
               "linkedIns": [ "https://www.linkedin.com/company/apifytech/" ],
               "twitters": [ "https://x.com/apify" ],
            },
            {
               "url": "https://apify.com/jobs",
               "domain": "apify.com",
            }
        ]

    Returns:
        response (str): Summarized data.
        
    Raises:
        LLMError: If the summarization operation fails.
    """
    try:
        logger.info('Summarizing contact information')
        return str(await llm.apredict(PROMPT_SUMMARIZE, scraped_data=contact_information))
    except Exception as e:
        raise LLMError(f'Failed to summarize contact information: {str(e)}', e) from e