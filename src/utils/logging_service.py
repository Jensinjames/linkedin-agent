"""Structured logging service for the LinkedIn agent."""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in {'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage'}:
                log_data[key] = value
        
        return json.dumps(log_data, default=str)


class LoggingService:
    """Centralized logging service with structured output."""
    
    def __init__(self, name: str = 'linkedin-agent', level: str = 'INFO'):
        """
        Initialize logging service.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create console handler with structured formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context."""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        self.logger.debug(message, extra=kwargs)
    
    def log_service_call(self, service: str, method: str, **kwargs):
        """Log service method calls with context."""
        self.info(f"Service call: {service}.{method}", 
                 service=service, method=method, **kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        self.info(f"Performance: {operation} completed in {duration:.3f}s",
                 operation=operation, duration=duration, **kwargs)
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """Log error with additional context."""
        self.error(f"Error occurred: {str(error)}", 
                  error_type=type(error).__name__, 
                  error_message=str(error),
                  **context)


# Global logging service instance
logging_service = LoggingService()
