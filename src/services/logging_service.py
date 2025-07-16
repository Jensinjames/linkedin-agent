"""Centralized logging configuration for the LinkedIn agent."""

import logging
import sys
from typing import Dict, Any
from ..config.settings import config


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with context."""
    
    def __init__(self):
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information."""
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra context if available
        if hasattr(record, 'query'):
            log_data['query'] = getattr(record, 'query')
        if hasattr(record, 'processing_method'):
            log_data['processing_method'] = getattr(record, 'processing_method')
        if hasattr(record, 'actor_id'):
            log_data['actor_id'] = getattr(record, 'actor_id')
        if hasattr(record, 'record_count'):
            log_data['record_count'] = getattr(record, 'record_count')
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Format as key=value pairs for better readability
        formatted_parts = []
        for key, value in log_data.items():
            if isinstance(value, str) and ' ' in value:
                formatted_parts.append(f'{key}="{value}"')
            else:
                formatted_parts.append(f'{key}={value}')
        
        return ' '.join(formatted_parts)


class LinkedInAgentLogger:
    """Centralized logger for the LinkedIn agent with structured logging."""
    
    def __init__(self, name: str = 'linkedin-agent'):
        """Initialize the structured logger."""
        self.logger = logging.getLogger(name)
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging with structured formatter."""
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Set log level from config
        level = getattr(logging, config.log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Set structured formatter
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def info(self, message: str, **context):
        """Log info message with optional context."""
        self._log_with_context(logging.INFO, message, context)
    
    def warning(self, message: str, **context):
        """Log warning message with optional context."""
        self._log_with_context(logging.WARNING, message, context)
    
    def error(self, message: str, **context):
        """Log error message with optional context."""
        self._log_with_context(logging.ERROR, message, context)
    
    def debug(self, message: str, **context):
        """Log debug message with optional context."""
        self._log_with_context(logging.DEBUG, message, context)
    
    def _log_with_context(self, level: int, message: str, context: Dict[str, Any]):
        """Log message with structured context."""
        # Create log record
        record = self.logger.makeRecord(
            self.logger.name, level, '', 0, message, (), None
        )
        
        # Add context as extra attributes
        for key, value in context.items():
            setattr(record, key, value)
        
        self.logger.handle(record)


# Global logger instance
agent_logger = LinkedInAgentLogger()


def get_logger(name: str | None = None) -> LinkedInAgentLogger:
    """Get a logger instance for the specified module."""
    if name:
        return LinkedInAgentLogger(f'linkedin-agent.{name}')
    return agent_logger
