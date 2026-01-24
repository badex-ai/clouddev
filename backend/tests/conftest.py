import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from main import app
import sys
from pathlib import Path
from datetime import datetime, timezone
from faker import Faker
import json
import uuid
from models.models import UserRole 
from utils.error_handler import AppError, ErrorCode

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.db import get_db, get_redis

fake = Faker()


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    
    # In-memory cache to simulate Redis behavior
    _cache = {}
    
    # Mock Redis operations with realistic behavior
    async def mock_get(key):
        return _cache.get(key)
    
    async def mock_set(key, value, *args, **kwargs):
        _cache[key] = value
        return True
    
    async def mock_setex(key, time, value):
        _cache[key] = value
        return True
    
    async def mock_delete(key):
        if key in _cache:
            del _cache[key]
            return 1
        return 0
    
    async def mock_exists(key):
        return 1 if key in _cache else 0
    
    # Assign side_effects for realistic behavior
    mock.get = AsyncMock(side_effect=mock_get)
    mock.set = AsyncMock(side_effect=mock_set)
    mock.setex = AsyncMock(side_effect=mock_setex)
    mock.delete = AsyncMock(side_effect=mock_delete)
    mock.exists = AsyncMock(side_effect=mock_exists)
    mock.close = AsyncMock(return_value=None)
    mock.ping = AsyncMock(return_value=True)
    
    # Context manager support
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    
    # Expose cache for test assertions
    mock._test_cache = _cache
    
    return mock


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    
    # CRITICAL: Create ONE query mock that will be reused
    query_mock = MagicMock()
    
    # Make query() ALWAYS return the same query_mock instance
    session.query = MagicMock(return_value=query_mock)
    
    query_mock.filter = MagicMock(return_value=query_mock)
    query_mock.filter_by = MagicMock(return_value=query_mock)
    query_mock.options = MagicMock(return_value=query_mock)
    query_mock.offset = MagicMock(return_value=query_mock)
    query_mock.limit = MagicMock(return_value=query_mock)
    query_mock.order_by = MagicMock(return_value=query_mock)
    query_mock.join = MagicMock(return_value=query_mock)
    query_mock.outerjoin = MagicMock(return_value=query_mock)
    query_mock.group_by = MagicMock(return_value=query_mock)
    query_mock.distinct = MagicMock(return_value=query_mock)
    
    # Terminal operations (these execute the query)
    query_mock.first = MagicMock(return_value=None)
    query_mock.all = MagicMock(return_value=[])
    query_mock.one = MagicMock(return_value=None)
    query_mock.one_or_none = MagicMock(return_value=None)
    query_mock.count = MagicMock(return_value=0)
    query_mock.scalar = MagicMock(return_value=None)
    
    # Update/Delete operations
    query_mock.update = MagicMock(return_value=1)
    query_mock.delete = MagicMock(return_value=1)
    
    def mock_add(obj):
        if not hasattr(obj, 'id') or obj.id is None:
            obj.id = fake.random_int(min=1, max=999999)
        
        if hasattr(obj, 'public_id') and obj.public_id is None:
            obj.public_id = str(uuid.uuid4())
        
        if hasattr(obj, 'created_at') and obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)
        if hasattr(obj, 'updated_at') and obj.updated_at is None:
            obj.updated_at = datetime.now(timezone.utc)
    
    session.add = MagicMock(side_effect=mock_add)
    session.add_all = MagicMock(side_effect=lambda objs: [mock_add(obj) for obj in objs])
    
    def mock_refresh(obj):
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = fake.random_int(min=1, max=999999)
        if hasattr(obj, 'public_id') and obj.public_id is None:
            obj.public_id = str(uuid.uuid4())
    
    session.refresh = MagicMock(side_effect=mock_refresh)
    
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    session.flush = MagicMock()
    session.delete = MagicMock()
    session.execute = MagicMock()
    session.merge = MagicMock()
    session.expunge = MagicMock()
    session.expunge_all = MagicMock()
    session.begin = MagicMock()
    session.begin_nested = MagicMock()
    
    return session


@pytest.fixture
def mock_user_factory():
    def factory(**kwargs):
        defaults = {
            "id": kwargs.get("id", fake.random_int(min=1, max=999999)),  # Database ID
            "public_id": kwargs.get("public_id", str(uuid.uuid4())),  # UUID string
            "email": kwargs.get("email", fake.email()),
            "name": kwargs.get("name", fake.first_name()),
            "family_name": kwargs.get("family_name", fake.last_name()),
            "family_id": kwargs.get("family_id", str(uuid.uuid4())),  # UUID string
            "username": kwargs.get("username", fake.user_name()),
            "role": UserRole.member,
            "is_active": kwargs.get("is_active", True),
            "password_hash": kwargs.get("password_hash", "hashed_password"),
            "created_at": kwargs.get("created_at", datetime.now(timezone.utc)),
            "updated_at": kwargs.get("updated_at", datetime.now(timezone.utc)),
        }
        class MockUser:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        return MockUser(defaults)
    return factory


@pytest.fixture
def mock_family_factory():
    def factory(**kwargs):
        defaults = {
            "id": kwargs.get("id", fake.random_int(min=1, max=999999)),  # Database ID
            "public_id": kwargs.get("public_id", str(uuid.uuid4())),  # UUID string
            "name": kwargs.get("name", f"The {fake.last_name()} Family"),
            "users": kwargs.get("users", []),
            "created_at": kwargs.get("created_at", datetime.now(timezone.utc)),
            "updated_at": kwargs.get("updated_at", datetime.now(timezone.utc)),
        }
        class MockFamily:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        return MockFamily(defaults)
    return factory


@pytest.fixture
def client(mock_redis, mock_db_session):
    # Set overrides before creating TestClient
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_redis] = lambda: mock_redis
    
    # Mock Celery tasks and Auth0 HTTP calls
    with patch("controllers.tasks.send_verification_email_task") as mock_verify, \
         patch("controllers.tasks.send_welcome_email_task") as mock_welcome, \
         patch("controllers.tasks.send_password_reset_task") as mock_reset, \
         patch("controllers.auth_controller.create_auth0_user") as mock_auth0_auth, \
         patch("controllers.user_controller.create_auth0_user") as mock_auth0_user, \
         patch("controllers.user_controller.create_password_reset_ticket") as mock_reset_ticket, \
         patch("controllers.user_controller.get_management_api_token") as mock_m2m_token, \
         patch("utils.utils.get_management_api_token") as mock_utils_token:
        
        async def mock_get_token():
            return f"mock_m2m_token_{uuid.uuid4().hex[:16]}"
        
        mock_m2m_token.side_effect = mock_get_token
        mock_utils_token.side_effect = mock_get_token

        async def mock_create_auth0_user_auth(email, password, name, family_name):
            return {
                "user_id": f"auth0|{uuid.uuid4().hex[:24]}",
                "email": email,
                "name": name,
                "family_name": family_name,
                "email_verified": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        
        async def mock_create_auth0_user_member(email, name, family_name, family_id, m2m_token):
            return (
                f"auth0|{uuid.uuid4().hex[:24]}",
                m2m_token
            )
        
        async def mock_create_reset_ticket(user_id, m2m_token):
            return f"https://example.com/reset?ticket={uuid.uuid4().hex}"
        
        mock_auth0_auth.side_effect = mock_create_auth0_user_auth
        mock_auth0_user.side_effect = mock_create_auth0_user_member
        mock_reset_ticket.side_effect = mock_create_reset_ticket

        mock_verify.delay = MagicMock(return_value=MagicMock(id="task-verify-123", status="PENDING"))
        mock_welcome.delay = MagicMock(return_value=MagicMock(id="task-welcome-123", status="PENDING"))
        mock_reset.delay = MagicMock(return_value=MagicMock(id="task-reset-123", status="PENDING"))
        
        mock_verify.return_value = MagicMock(id="task-verify-123")
        mock_welcome.return_value = MagicMock(id="task-welcome-123")
        mock_reset.return_value = MagicMock(id="task-reset-123")
        
        with TestClient(app) as test_client:
            yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Generate realistic test data using Faker."""
    return {
        "id": fake.random_int(min=1, max=999999),
        "public_id": str(uuid.uuid4()),
        "email": fake.email(),
        "name": fake.first_name(),
        "family_name": fake.last_name(),
        "family_id": str(uuid.uuid4()),
        "username": fake.user_name(),
        "role": "member",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_task_data():

    """Generate sample task data."""
    # CRITICAL FIX: Use future date to avoid validation error
    future_date = datetime.now(timezone.utc)
    # Add 1 day to ensure it's in the future
    from datetime import timedelta
    future_date = future_date + timedelta(days=1)

   

    return {
        "id": fake.random_int(min=1, max=999999),
        "public_id": str(uuid.uuid4()),
        "title": fake.sentence(),
        "description": fake.paragraph(),
        "creator_id": str(uuid.uuid4()),
        "assignee_id": str(uuid.uuid4()),
        "family_id": str(uuid.uuid4()),
        "due_date": future_date.isoformat(), 
        "status": "initialised",
        "checklist": [
            {"id": 1, "title": fake.sentence(), "completed": False},
            {"id": 2, "title": fake.sentence(), "completed": True},
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_family_data():
    """Generate sample family data."""
    return {
        "id": fake.random_int(min=1, max=999999),
        "public_id": str(uuid.uuid4()),
        "name": fake.last_name() + " Family",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def benchmark_user_data(sample_user_data):
    """Generate multiple user records for performance testing."""
    return [
        {
            **sample_user_data, 
            "id": fake.random_int(min=1, max=999999),
            "public_id": str(uuid.uuid4()),
            "email": fake.email()
        }
        for _ in range(100)
    ]


@pytest.fixture
def benchmark_task_data(sample_task_data):
    """Generate multiple task records for performance testing."""
    return [
        {
            **sample_task_data,
            "id": fake.random_int(min=1, max=999999), 
            "public_id": str(uuid.uuid4())
        }
        for _ in range(100)
    ]