"""Enhanced LinkedIn crawler with advanced anti-detection and database features."""

import asyncio
import logging
import random
import re
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime, timedelta

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger('linkedin_crawler')

@dataclass
class ProxyConfig:
    """Configuration for proxy settings."""
    server: str
    username: Optional[str] = None
    password: Optional[str] = None

@dataclass
class AntiDetectionConfig:
    """Configuration for anti-detection measures."""
    min_delay: int = 2
    max_delay: int = 8
    scroll_pause_time: float = 0.5
    human_like_typing_delay: int = 100
    viewport_width_range: tuple = (1200, 1920)
    viewport_height_range: tuple = (800, 1080)
    user_agents: List[str] = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
            ]

class RateLimiter:
    """Rate limiter to manage request frequency."""
    
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    async def wait_if_needed(self):
        """Wait if we're making requests too frequently."""
        now = time.time()
        
        # Remove old requests (older than 1 minute)
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # If we've made too many requests, wait
        if len(self.request_times) >= self.requests_per_minute:
            oldest_request = min(self.request_times)
            wait_time = 60 - (now - oldest_request)
            if wait_time > 0:
                logger.info(f"Rate limiting: waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(now)

class LinkedInCrawler:
    """LinkedIn crawler using Playwright for scraping profiles and company pages."""
    
    def __init__(
        self, 
        headless: bool = True, 
        timeout: int = 30000,
        proxy_config: Optional[ProxyConfig] = None,
        anti_detection_config: Optional[AntiDetectionConfig] = None,
        requests_per_minute: int = 10
    ):
        self.headless = headless
        self.timeout = timeout
        self.proxy_config = proxy_config
        self.anti_detection_config = anti_detection_config or AntiDetectionConfig()
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        
        # Enhanced browser args for better anti-detection
        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-field-trial-config',
            '--disable-hang-monitor',
            '--disable-ipc-flooding-protection',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--disable-translate',
            '--disable-windows10-custom-titlebar',
            '--metrics-recording-only',
            '--no-default-browser-check',
            '--no-first-run',
            '--safebrowsing-disable-auto-update',
            '--enable-automation',
            '--password-store=basic',
            '--use-mock-keychain'
        ]
        
        launch_options = {
            'headless': self.headless,
            'args': browser_args
        }
        
        # Add proxy if configured
        if self.proxy_config:
            launch_options['proxy'] = {
                'server': self.proxy_config.server,
                'username': self.proxy_config.username,
                'password': self.proxy_config.password
            }
        
        self.browser = await self.playwright.chromium.launch(**launch_options)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()
    
    async def _create_page(self) -> Page:
        """Create a new page with anti-detection measures."""
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")
            
        page = await self.browser.new_page()
        
        # Randomize user agent
        user_agent = random.choice(self.anti_detection_config.user_agents)
        await page.set_user_agent(user_agent)
        
        # Randomize viewport size
        width = random.randint(*self.anti_detection_config.viewport_width_range)
        height = random.randint(*self.anti_detection_config.viewport_height_range)
        await page.set_viewport_size({"width": width, "height": height})
        
        # Set realistic headers
        await page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Advanced anti-detection script
        await page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            
            // Mock chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Override the `outerHeight` and `outerWidth` properties to match the viewport
            Object.defineProperty(window, 'outerHeight', {
                get: () => window.innerHeight,
            });
            Object.defineProperty(window, 'outerWidth', {
                get: () => window.innerWidth,
            });
            
            // Mock device memory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
            });
            
            // Mock hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 4,
            });
        """)
        
        return page
    
    async def _simulate_human_behavior(self, page: Page):
        """Simulate human-like behavior on the page."""
        try:
            # Random scrolling
            await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        let totalHeight = 0;
                        const distance = 100;
                        const timer = setInterval(() => {
                            const scrollHeight = document.body.scrollHeight;
                            window.scrollBy(0, distance);
                            totalHeight += distance;
                            
                            if(totalHeight >= scrollHeight / 3){
                                clearInterval(timer);
                                resolve();
                            }
                        }, 100);
                    });
                }
            """)
            
            # Random pause
            delay = random.uniform(
                self.anti_detection_config.min_delay, 
                self.anti_detection_config.max_delay
            )
            await asyncio.sleep(delay)
            
            # Random mouse movement
            await page.mouse.move(
                random.randint(0, 800),
                random.randint(0, 600)
            )
            
        except Exception as e:
            logger.warning(f"Error simulating human behavior: {e}")
    
    async def _extract_profile_data(self, page: Page, url: str) -> Dict[str, Any]:
        """Extract data from a LinkedIn profile page."""
        try:
            # Wait for the page to load
            await page.wait_for_load_state('networkidle', timeout=self.timeout)
            
            # Extract basic profile information
            profile_data = {
                'url': url,
                'type': 'profile',
                'name': None,
                'headline': None,
                'location': None,
                'about': None,
                'experience': [],
                'education': [],
                'skills': [],
                'contact_info': {},
                'scraped_at': None
            }
            
            # Extract name
            try:
                name_element = await page.wait_for_selector('h1.text-heading-xlarge', timeout=5000)
                profile_data['name'] = await name_element.inner_text()
            except PlaywrightTimeoutError:
                logger.warning(f"Could not find name element for {url}")
            
            # Extract headline
            try:
                headline_element = await page.query_selector('.text-body-medium.break-words')
                if headline_element:
                    profile_data['headline'] = await headline_element.inner_text()
            except Exception as e:
                logger.warning(f"Could not extract headline: {e}")
            
            # Extract location
            try:
                location_element = await page.query_selector('.text-body-small.inline.t-black--light.break-words')
                if location_element:
                    profile_data['location'] = await location_element.inner_text()
            except Exception as e:
                logger.warning(f"Could not extract location: {e}")
            
            # Extract about section
            try:
                about_element = await page.query_selector('[data-generated-suggestion-target="urn:li:member"] .full-width')
                if about_element:
                    profile_data['about'] = await about_element.inner_text()
            except Exception as e:
                logger.warning(f"Could not extract about section: {e}")
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error extracting profile data from {url}: {e}")
            return {'url': url, 'type': 'profile', 'error': str(e)}
    
    async def _extract_company_data(self, page: Page, url: str) -> Dict[str, Any]:
        """Extract data from a LinkedIn company page."""
        try:
            await page.wait_for_load_state('networkidle', timeout=self.timeout)
            
            company_data = {
                'url': url,
                'type': 'company',
                'name': None,
                'tagline': None,
                'description': None,
                'industry': None,
                'company_size': None,
                'headquarters': None,
                'website': None,
                'specialties': [],
                'founded': None,
                'scraped_at': None
            }
            
            # Extract company name
            try:
                name_element = await page.wait_for_selector('h1.org-top-card-summary__title', timeout=5000)
                company_data['name'] = await name_element.inner_text()
            except PlaywrightTimeoutError:
                # Try alternative selector
                try:
                    name_element = await page.query_selector('.org-top-card-summary__title')
                    if name_element:
                        company_data['name'] = await name_element.inner_text()
                except Exception:
                    logger.warning(f"Could not find company name for {url}")
            
            # Extract tagline
            try:
                tagline_element = await page.query_selector('.org-top-card-summary__tagline')
                if tagline_element:
                    company_data['tagline'] = await tagline_element.inner_text()
            except Exception as e:
                logger.warning(f"Could not extract tagline: {e}")
            
            # Extract description
            try:
                desc_element = await page.query_selector('.break-words.white-space-pre-wrap.t-14.t-black--light.t-normal')
                if desc_element:
                    company_data['description'] = await desc_element.inner_text()
            except Exception as e:
                logger.warning(f"Could not extract description: {e}")
            
            # Extract company details from the info section
            try:
                info_elements = await page.query_selector_all('.org-page-details__definition-text')
                labels = await page.query_selector_all('.org-page-details__definition-term')
                
                for i, label_element in enumerate(labels):
                    if i < len(info_elements):
                        label = await label_element.inner_text()
                        value = await info_elements[i].inner_text()
                        
                        if 'industry' in label.lower():
                            company_data['industry'] = value
                        elif 'company size' in label.lower():
                            company_data['company_size'] = value
                        elif 'headquarters' in label.lower():
                            company_data['headquarters'] = value
                        elif 'founded' in label.lower():
                            company_data['founded'] = value
                        elif 'specialties' in label.lower():
                            company_data['specialties'] = [s.strip() for s in value.split(',')]
            except Exception as e:
                logger.warning(f"Could not extract company details: {e}")
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error extracting company data from {url}: {e}")
            return {'url': url, 'type': 'company', 'error': str(e)}
    
    async def scrape_url(self, url: str, save_to_db: bool = True, db_manager=None) -> Dict[str, Any]:
        """Scrape a single LinkedIn URL."""
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")
        
        logger.info(f"Scraping LinkedIn URL: {url}")
        
        # Apply rate limiting
        await self.rate_limiter.wait_if_needed()
        
        page = await self._create_page()
        
        try:
            # Navigate to the URL
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            # Simulate human behavior
            await self._simulate_human_behavior(page)
            
            # Determine if this is a profile or company page
            if '/in/' in url or '/profile/' in url:
                result = await self._extract_profile_data(page, url)
            elif '/company/' in url:
                result = await self._extract_company_data(page, url)
            else:
                # Generic extraction for other LinkedIn pages
                title = await page.title()
                content = await page.content()
                result = {
                    'url': url,
                    'type': 'generic',
                    'title': title,
                    'content_length': len(content),
                    'scraped_at': None
                }
            
            # Add timestamp
            from datetime import datetime
            result['scraped_at'] = datetime.utcnow().isoformat()
            
            # Save to database if requested
            if save_to_db and db_manager and not result.get('error'):
                try:
                    if result.get('type') == 'profile':
                        success = db_manager.save_profile(result)
                        logger.info(f"Profile saved to database: {success}")
                    elif result.get('type') == 'company':
                        success = db_manager.save_company(result)
                        logger.info(f"Company saved to database: {success}")
                except Exception as e:
                    logger.warning(f"Failed to save to database: {e}")
            
            return result
            
        except PlaywrightTimeoutError:
            logger.error(f"Timeout while loading {url}")
            return {'url': url, 'error': 'Timeout while loading page'}
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {'url': url, 'error': str(e)}
        finally:
            await page.close()


async def run_linkedin_crawler(
    query: str, 
    max_depth: int = 2, 
    include_socials: bool = True,
    save_to_db: bool = True,
    db_path: str = "linkedin_data.db",
    proxy_config: Optional[ProxyConfig] = None,
    anti_detection_config: Optional[AntiDetectionConfig] = None,
    requests_per_minute: int = 10
) -> Dict[str, Any]:
    """Run LinkedIn crawler with the given query and parameters.
    
    Args:
        query: URL or search query for LinkedIn
        max_depth: Maximum depth for crawling (currently not used for recursive crawling)
        include_socials: Whether to include social media links (currently not implemented)
        save_to_db: Whether to save results to database
        db_path: Path to SQLite database file
        proxy_config: Optional proxy configuration
        anti_detection_config: Optional anti-detection configuration
        requests_per_minute: Rate limiting parameter
    
    Returns:
        Dictionary containing scraped data and job information
    """
    logger.info(f"Starting LinkedIn crawler with query: {query}")
    
    # Initialize database if needed
    db_manager = None
    job_id = None
    if save_to_db:
        try:
            from ..database.models import DatabaseManager
            db_manager = DatabaseManager(db_path)
            logger.info(f"Database initialized at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            save_to_db = False
    
    # Extract URLs from query
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, query)
    
    if not urls:
        # If no URL found, assume the query is a LinkedIn URL or construct one
        if 'linkedin.com' in query:
            urls = [query.strip()]
        else:
            # This is a fallback - in a real implementation, you might want to
            # search LinkedIn for the query terms
            return {
                'query': query,
                'max_depth': max_depth,
                'include_socials': include_socials,
                'error': 'No valid LinkedIn URL found in query. Please provide a direct LinkedIn URL.',
                'scraped_data': [],
                'job_id': None
            }
    
    # Create scrape job in database
    if db_manager:
        try:
            job_id = db_manager.create_scrape_job(query, len(urls[:max_depth]))
            db_manager.update_scrape_job(job_id, status='running')
        except Exception as e:
            logger.warning(f"Failed to create scrape job: {e}")
    
    scraped_data = []
    errors = []
    scraped_count = 0
    failed_count = 0
    
    try:
        # Initialize crawler with enhanced configuration
        crawler_config = {
            'headless': True,
            'timeout': 30000,
            'requests_per_minute': requests_per_minute
        }
        
        if proxy_config:
            crawler_config['proxy_config'] = proxy_config
        if anti_detection_config:
            crawler_config['anti_detection_config'] = anti_detection_config
        
        async with LinkedInCrawler(**crawler_config) as crawler:
            for i, url in enumerate(urls[:max_depth]):
                try:
                    logger.info(f"Scraping URL {i+1}/{len(urls[:max_depth])}: {url}")
                    
                    # Check if we already have this data in the database
                    existing_data = None
                    if db_manager:
                        if '/in/' in url or '/profile/' in url:
                            existing_data = db_manager.get_profile(url)
                        elif '/company/' in url:
                            existing_data = db_manager.get_company(url)
                    
                    if existing_data:
                        logger.info(f"Using cached data for {url}")
                        result = existing_data
                        result['cached'] = True
                    else:
                        # Scrape fresh data
                        result = await crawler.scrape_url(url, save_to_db=save_to_db, db_manager=db_manager)
                        result['cached'] = False
                    
                    scraped_data.append(result)
                    
                    if result.get('error'):
                        failed_count += 1
                    else:
                        scraped_count += 1
                    
                    # Update job progress
                    if db_manager and job_id:
                        db_manager.update_scrape_job(
                            job_id, 
                            scraped_urls=scraped_count, 
                            failed_urls=failed_count
                        )
                    
                    # Add delay between requests (unless it's the last URL)
                    if i < len(urls[:max_depth]) - 1:
                        delay = random.uniform(2, 5)  # Random delay between 2-5 seconds
                        logger.info(f"Waiting {delay:.1f} seconds before next request...")
                        await asyncio.sleep(delay)
                        
                except Exception as e:
                    error_msg = f"Failed to scrape {url}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    failed_count += 1
                    
                    # Update job progress
                    if db_manager and job_id:
                        db_manager.update_scrape_job(
                            job_id, 
                            scraped_urls=scraped_count, 
                            failed_urls=failed_count,
                            errors=errors
                        )
                    
    except Exception as e:
        error_msg = f"Failed to initialize crawler: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    # Update final job status
    if db_manager and job_id:
        try:
            final_status = 'completed' if scraped_count > 0 else 'failed'
            db_manager.update_scrape_job(
                job_id,
                status=final_status,
                scraped_urls=scraped_count,
                failed_urls=failed_count,
                errors=errors
            )
        except Exception as e:
            logger.warning(f"Failed to update final job status: {e}")
    
    result = {
        'query': query,
        'max_depth': max_depth,
        'include_socials': include_socials,
        'scraped_data': scraped_data,
        'errors': errors,
        'success': len(scraped_data) > 0,
        'total_scraped': scraped_count,
        'total_failed': failed_count,
        'job_id': job_id,
        'database_enabled': save_to_db
    }
    
    logger.info(f"Crawler completed. Scraped: {scraped_count}, Failed: {failed_count}, Job ID: {job_id}")
    return result


# Legacy compatibility for the original function
async def run_linkedin_crawler_legacy(
    query: str,
    max_depth: int = 2,
    include_socials: bool = True,
) -> Dict[str, Any]:
    """
    Legacy LinkedIn crawler for backward compatibility.
    
    This maintains the original behavior while using the new enhanced crawler.
    """
    from ..tools import call_contact_details_scraper
    
    urls = [part.strip() for part in query.split() if part.strip()]
    start_urls = [{"url": url} for url in urls if url.startswith("http")]
    if not start_urls:
        raise ValueError("No LinkedIn URLs provided")

    for attempt in range(3):
        try:
            data = await call_contact_details_scraper(start_urls, max_depth=max_depth)
            break
        except Exception as e:
            logger.warning(
                "Contact Details Scraper failed on attempt %d: %s",
                attempt + 1,
                e,
            )
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)

    if not include_socials:
        for record in data:
            for field in (
                "linkedIns",
                "twitters",
                "facebooks",
                "instagrams",
                "youtubes",
            ):
                record.pop(field, None)

    return {"query": query, "results": data}

