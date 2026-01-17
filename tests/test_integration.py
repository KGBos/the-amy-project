"""
Integration tests for Amy
Tests full chat cycle, error paths, and edge cases
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from amy.core.amy import Amy, AmyProvider
from amy.core.errors import InputValidationError, TransientError, RateLimitError
from amy.config import MAX_MESSAGE_LENGTH


class TestAmyInputValidation:
    """Tests for input validation in Amy."""
    
    @pytest.fixture
    def mock_amy(self):
        """Create Amy with mocked dependencies."""
        with patch('amy.core.amy.ConversationDB'), \
             patch('amy.core.amy.LTM'), \
             patch('amy.core.amy.Runner'), \
             patch('amy.core.amy.SqliteSessionService'):
            amy = Amy()
            return amy
    
    @pytest.mark.asyncio
    async def test_empty_message_returns_friendly_error(self, mock_amy):
        """Test that empty messages are handled gracefully."""
        response = await mock_amy.chat("test_session", "", user_id="user1")
        assert "didn't receive" in response.lower()
    
    @pytest.mark.asyncio
    async def test_whitespace_only_message_returns_friendly_error(self, mock_amy):
        """Test that whitespace-only messages are handled."""
        response = await mock_amy.chat("test_session", "   ", user_id="user1")
        assert "didn't receive" in response.lower()
    
    @pytest.mark.asyncio
    async def test_long_message_returns_friendly_error(self, mock_amy):
        """Test that overly long messages are rejected."""
        long_message = "x" * (MAX_MESSAGE_LENGTH + 1)
        response = await mock_amy.chat("test_session", long_message, user_id="user1")
        assert "too long" in response.lower()


class TestAmyProvider:
    """Tests for AmyProvider singleton pattern."""
    
    def test_get_returns_amy_instance(self):
        """Test that get() returns an Amy instance."""
        with patch('amy.core.amy.ConversationDB'), \
             patch('amy.core.amy.LTM'), \
             patch('amy.core.amy.Runner'), \
             patch('amy.core.amy.SqliteSessionService'):
            
            AmyProvider.reset()  # Ensure clean state
            amy = AmyProvider.get()
            assert isinstance(amy, Amy)
            AmyProvider.reset()  # Clean up
    
    def test_get_returns_same_instance(self):
        """Test that get() returns the same instance on repeated calls."""
        with patch('amy.core.amy.ConversationDB'), \
             patch('amy.core.amy.LTM'), \
             patch('amy.core.amy.Runner'), \
             patch('amy.core.amy.SqliteSessionService'):
            
            AmyProvider.reset()
            amy1 = AmyProvider.get()
            amy2 = AmyProvider.get()
            assert amy1 is amy2
            AmyProvider.reset()
    
    def test_reset_clears_instance(self):
        """Test that reset() clears the singleton instance."""
        with patch('amy.core.amy.ConversationDB'), \
             patch('amy.core.amy.LTM'), \
             patch('amy.core.amy.Runner'), \
             patch('amy.core.amy.SqliteSessionService'):
            
            AmyProvider.reset()
            amy1 = AmyProvider.get()
            AmyProvider.reset()
            amy2 = AmyProvider.get()
            assert amy1 is not amy2
            AmyProvider.reset()


class TestErrorTypes:
    """Tests for error type classifications."""
    
    def test_input_validation_error_not_retryable(self):
        """Test that InputValidationError is not retryable."""
        error = InputValidationError("test")
        assert not error.is_retryable
    
    def test_transient_error_is_retryable(self):
        """Test that TransientError is retryable."""
        error = TransientError("test")
        assert error.is_retryable
    
    def test_rate_limit_error_is_retryable(self):
        """Test that RateLimitError is retryable."""
        error = RateLimitError()
        assert error.is_retryable
    
    def test_error_user_message(self):
        """Test that errors have user-friendly messages."""
        error = RateLimitError()
        assert error.user_message
        assert "overwhelmed" in error.user_message.lower() or "try again" in error.user_message.lower()


class TestCleanResponse:
    """Tests for response cleaning."""
    
    @pytest.fixture
    def amy(self):
        """Create Amy with mocked dependencies."""
        with patch('amy.core.amy.ConversationDB'), \
             patch('amy.core.amy.LTM'), \
             patch('amy.core.amy.Runner'), \
             patch('amy.core.amy.SqliteSessionService'):
            return Amy()
    
    def test_clean_response_removes_planner_tags(self, amy):
        """Test that planner tags are removed from responses."""
        dirty = "/*PLANNING*/Hello/*REASONING*/World/*FINAL_ANSWER*/"
        clean = amy._clean_response(dirty)
        assert "PLANNING" not in clean
        assert "REASONING" not in clean
        assert "FINAL_ANSWER" not in clean
        assert "Hello" in clean
        assert "World" in clean
    
    def test_clean_response_strips_whitespace(self, amy):
        """Test that whitespace is stripped."""
        dirty = "  Hello World  "
        clean = amy._clean_response(dirty)
        assert clean == "Hello World"
