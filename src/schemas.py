from pydantic import BaseModel, Field, ValidationError

class ActorInput(BaseModel):
    """Input schema for the crawler."""

    query: str = Field(..., description="LinkedIn URLs separated by whitespace")
    modelName: str = Field(default="gpt-4o", description="OpenAI model name")
    maxDepth: int = Field(default=2, ge=1, description="Crawling depth")
    includeSocials: bool = Field(default=True, description="Return social profiles")
