from pydantic import BaseModel, Field, field_validator
import re

class ActorInput(BaseModel):
    """Input schema for the crawler."""

    query: str = Field(..., description="LinkedIn URLs separated by whitespace")
    modelName: str = Field(default="gpt-4o", description="OpenAI model name")
    maxDepth: int = Field(default=2, ge=1, description="Crawling depth")
    includeSocials: bool = Field(default=True, description="Return social profiles")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate that query contains valid URLs or descriptive text."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Check if query contains URLs
        urls = [word for word in v.split() if word.startswith(('http://', 'https://'))]
        if urls:
            # Validate URL format for LinkedIn or other domains
            url_pattern = re.compile(
                r'^https?://(?:www\.)?(?:linkedin\.com|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/'
            )
            for url in urls:
                if not url_pattern.match(url):
                    raise ValueError(f"Invalid URL format: {url}")
        
        return v
