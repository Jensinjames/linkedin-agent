"""
Direct web scraping alternative that replaces Apify dependency.
Uses requests + BeautifulSoup for simple scraping without external services.
"""
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)

class SimpleWebScraper:
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_contact_details(self, url: str) -> Dict[str, Any]:
        """
        Simple contact details scraper that replaces Apify contact-info-scraper.
        Extracts basic contact information from web pages.
        """
        try:
            response = self._get_page(url)
            if not response:
                return {"error": f"Failed to fetch {url}"}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            contact_info = {
                "url": url,
                "title": self._extract_title(soup),
                "emails": self._extract_emails(soup),
                "phones": self._extract_phones(soup),
                "social_links": self._extract_social_links(soup, url),
                "description": self._extract_description(soup),
                "timestamp": time.time()
            }
            
            return contact_info
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {"url": url, "error": str(e)}
    
    def _get_page(self, url: str):
        """Get page with retries and delay"""
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay)
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts: {e}")
                    return None
                time.sleep(self.delay * (attempt + 1))
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_emails(self, soup: BeautifulSoup) -> List[str]:
        """Extract email addresses using simple patterns"""
        emails = set()
        
        # Search in text content
        text = soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails.update(re.findall(email_pattern, text))
        
        # Search in href attributes
        try:
            for link in soup.find_all('a'):
                href = str(link.get('href', ''))
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0]
                    emails.add(email)
        except Exception:
            pass  # Skip if any parsing errors
        
        return list(emails)
    
    def _extract_phones(self, soup: BeautifulSoup) -> List[str]:
        """Extract phone numbers using simple patterns"""
        phones = set()
        
        text = soup.get_text()
        # Simple phone patterns
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        for pattern in phone_patterns:
            phones.update(re.findall(pattern, text))
        
        # Search in href attributes
        try:
            for link in soup.find_all('a'):
                href = str(link.get('href', ''))
                if href.startswith('tel:'):
                    phone = href.replace('tel:', '')
                    phones.add(phone)
        except Exception:
            pass  # Skip if any parsing errors
        
        return list(phones)
    
    def _extract_social_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract social media links"""
        social_domains = [
            'linkedin.com', 'twitter.com', 'facebook.com', 'instagram.com',
            'youtube.com', 'github.com', 'tiktok.com'
        ]
        
        social_links = set()
        
        try:
            for link in soup.find_all('a'):
                href = str(link.get('href', ''))
                if href:
                    full_url = urljoin(base_url, href)
                    
                    for domain in social_domains:
                        if domain in full_url:
                            social_links.add(full_url)
                            break
        except Exception:
            pass  # Skip if any parsing errors
        
        return list(social_links)
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description"""
        try:
            # Try meta description first
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                content = meta_desc.get('content')
                if content:
                    return str(content).strip()
            
            # Try OpenGraph description
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc:
                content = og_desc.get('content')
                if content:
                    return str(content).strip()
            
            # Fallback to first paragraph
            first_p = soup.find('p')
            if first_p:
                return first_p.get_text().strip()[:200] + "..."
        except Exception:
            pass  # Skip if any parsing errors
        
        return ""

# Async wrapper for compatibility
async def call_contact_details_scraper(
    start_urls: List[Dict[str, Any]],
    max_requests_per_start_url: int = 5,
    max_depth: int = 2,
    same_domain: bool = True,
    deduplicate: bool = True,
) -> List[Dict]:
    """
    Async wrapper that replaces the Apify contact details scraper.
    This version uses simple web scraping instead of external services.
    """
    scraper = SimpleWebScraper()
    results = []
    
    for url_data in start_urls:
        url = url_data.get('url', '')
        if not url:
            continue
            
        logger.info(f"Scraping contact details from: {url}")
        contact_info = scraper.scrape_contact_details(url)
        results.append(contact_info)
        
        # Simple rate limiting
        time.sleep(1)
    
    # Remove duplicates if requested
    if deduplicate:
        seen_urls = set()
        deduplicated = []
        for result in results:
            url = result.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(result)
        results = deduplicated
    
    return results
