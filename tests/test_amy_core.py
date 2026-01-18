import pytest
import asyncio
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from google.genai.types import Content, Part
from google.adk.models import LlmResponse

from amy.core.amy import Amy

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.initialize = AsyncMock()
    db.get_recent_messages.return_value = []
    db.get_message_count.return_value = 0
    db.add_message.return_value = 1
    db.has_previous_conversations.return_value = False
    return db

@pytest.fixture
def mock_ltm():
    ltm = MagicMock()
    return ltm

@pytest.fixture
def mock_runner():
    runner = MagicMock()
    
    # Mock run_async to yield a response
    async def async_generator(*args, **kwargs):
        # Simulate a simple response content
        response_content = Content(parts=[Part(text="Hello from Mock Amy")])
        # We need to yield an object that has a .content attribute
        yield LlmResponse(content=response_content)
        
    runner.run_async = async_generator
    return runner

@pytest.fixture
def mock_session_service():
    service = MagicMock()
    service.get_session = AsyncMock(return_value=None)
    service.create_session = AsyncMock()
    return service

@pytest_asyncio.fixture
async def amy_instance_with_mocks(mock_db, mock_ltm, mock_runner, mock_session_service):
    # Patch dependencies
    with patch('amy.core.amy.ConversationDB', return_value=mock_db), \
         patch('amy.core.amy.LTM', return_value=mock_ltm), \
         patch('amy.core.amy.Runner', return_value=mock_runner), \
         patch('amy.core.amy.SqliteSessionService', return_value=mock_session_service):
        
        amy = Amy()
        # Initialize the brain components (async)
        await amy.initialize()
        
        # Ensure our mock runner wrapper is used
        amy.runner = mock_runner
        
        # Mock session
        mock_session = MagicMock()
        mock_session.state = {}
        mock_session_service.create_session.return_value = mock_session
        mock_session_service.get_session.return_value = mock_session
        
        return amy, mock_session

@pytest.mark.asyncio
async def test_chat_success(amy_instance_with_mocks, mock_runner):
    """Test successful chat flow (interaction with Runner)."""
    amy, mock_session = amy_instance_with_mocks
    session_id = "test_sess_1"
    user_id = "user_1"
    message = "Hello Amy"
    
    response = await amy.chat(session_id, message, user_id=user_id)
    
    # Verify response passed through
    assert response == "Hello from Mock Amy"
    
    # Verify Runner was called
    # We can't verify db calls here easily because they happen inside the real Runner/SessionService
    # and we mocked the SessionService. 
    # So we verify Amy -> Runner delegation via the response.
    # Note: mock_runner.run_async is a raw async generator here, so assert_called is not available.
    pass

@pytest.mark.asyncio
async def test_sqlite_session_service_persistence(mock_db):
    """Test the SqliteSessionService directly for persistence logic."""
    from amy.memory.session_service import SqliteSessionService
    from google.adk.sessions.session import Session, Event
    from google.genai.types import Content, Part
    
    service = SqliteSessionService(mock_db)
    
    # Create a session
    # ADK Session Pydantic fields: id, app_name, user_id, state(optional), events(optional)
    session = Session(
        id="s1", 
        app_name="amy",
        user_id="u1",
        events=[], 
        state={'platform': 'test'}
    )
    
    # Simulate an incoming User Event
    user_content = Content(role="user", parts=[Part(text="Hi")])
    user_event = Event(author="user", content=user_content)
    
    # Trigger append_event
    await service.append_event(session, user_event)
    
    # Verify User Message Persisted
    mock_db.add_message.assert_any_call("s1", "user", "Hi", "u1", "test")
    
    # Simulate a Model Event
    model_content = Content(role="model", parts=[Part(text="Hello")])
    model_event = Event(author="model", content=model_content)
    
    # Trigger append_event
    await service.append_event(session, model_event)
     
    # Verify Model Message Persisted
    mock_db.add_message.assert_any_call("s1", "assistant", "Hello", "u1", "test")
