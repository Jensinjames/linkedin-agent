"""Legacy agent module for backward compatibility."""

# Import the new implementation for backward compatibility
from .core.agent import run_agent

__all__ = ['run_agent']
