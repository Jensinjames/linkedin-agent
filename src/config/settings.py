"""Configuration settings for the LinkedIn agent."""

import os
from typing import Optional
from pydantic import BaseModel, Field


class ApifyConfig(BaseModel):
    """Configuration for Apify services."""
    
    token: Optional[str] = Field(default_factory=lambda: os.getenv('APIFY_TOKEN'))
    contact_details_actor_id: str = Field(default='vdrmota/contact-info-scraper')
    default_max_requests: int = Field(default=5)
    default_max_depth: int = Field(default=2)
    same_domain_default: bool = Field(default=True)
    deduplicate_default: bool = Field(default=True)


class LLMConfig(BaseModel):
    """Configuration for LLM services."""
    
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv('OPENAI_API_KEY'))
    default_model: str = Field(default='gpt-4o')
    temperature: float = Field(default=0.0)
    max_tokens: Optional[int] = Field(default=None)


class AgentConfig(BaseModel):
    """Configuration for agent behavior."""
    
    default_verbose: bool = Field(default=False)
    action_words: list[str] = Field(
        default=['summarize', 'analyze', 'find', 'extract', 'process', 'search']
    )


class AppConfig(BaseModel):
    """Main application configuration."""
    
    apify: ApifyConfig = Field(default_factory=ApifyConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    log_level: str = Field(default='INFO')
    
    def validate_config(self) -> list[str]:
        """
        Validate configuration and return list of validation errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not self.apify.token:
            errors.append("APIFY_TOKEN environment variable not set")
        
        if not self.llm.openai_api_key:
            errors.append("OPENAI_API_KEY environment variable not set")
        
        return errors


# Global configuration instance
config = AppConfig()
