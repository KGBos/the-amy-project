"""
Error types for Amy

Structured error handling with categorization for proper retry logic
and user-facing message generation.
"""

from enum import Enum
from typing import Optional


class ErrorType(Enum):
    """Classification of error types for handling logic."""
    TRANSIENT = "transient"    # Retry-able (network hiccup, temporary failure)
    PERMANENT = "permanent"    # Don't retry (invalid input, auth failure)
    RATE_LIMIT = "rate_limit"  # Back off and retry later


class AmyError(Exception):
    """
    Base error class for Amy with error classification.
    
    Attributes:
        error_type: Classification for retry/handling logic
        original: The original exception that caused this error
        user_message: Safe message to show to users
    """
    
    def __init__(
        self, 
        message: str, 
        error_type: ErrorType = ErrorType.PERMANENT,
        original: Optional[Exception] = None,
        user_message: Optional[str] = None
    ):
        self.error_type = error_type
        self.original = original
        self.user_message = user_message or "Something went wrong. Please try again."
        super().__init__(message)
    
    @property
    def is_retryable(self) -> bool:
        """Check if this error type should be retried."""
        return self.error_type in (ErrorType.TRANSIENT, ErrorType.RATE_LIMIT)


class RateLimitError(AmyError):
    """Rate limit exceeded - back off and retry."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        original: Optional[Exception] = None,
        retry_after: Optional[float] = None
    ):
        self.retry_after = retry_after
        super().__init__(
            message, 
            ErrorType.RATE_LIMIT, 
            original,
            "I'm a bit overwhelmed right now. Please try again in a moment."
        )


class TransientError(AmyError):
    """Temporary failure - worth retrying."""
    
    def __init__(
        self, 
        message: str, 
        original: Optional[Exception] = None
    ):
        super().__init__(
            message, 
            ErrorType.TRANSIENT, 
            original,
            "I had a brief hiccup. Let me try again."
        )


class MemoryError(AmyError):
    """Error accessing memory systems."""
    
    def __init__(
        self, 
        message: str, 
        original: Optional[Exception] = None,
        is_transient: bool = False
    ):
        error_type = ErrorType.TRANSIENT if is_transient else ErrorType.PERMANENT
        super().__init__(
            message, 
            error_type, 
            original,
            "I'm having trouble with my memory. Please try again."
        )


class InputValidationError(AmyError):
    """Invalid user input - don't retry, fix the input."""
    
    def __init__(self, message: str, user_message: Optional[str] = None):
        super().__init__(
            message, 
            ErrorType.PERMANENT, 
            None,
            user_message or message
        )
