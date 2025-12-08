import pytest
from fastapi import status
from unittest.mock import Mock, patch
from datetime import datetime, timezone, date
from models.models import UserRole
from faker import Faker
import uuid
from sqlalchemy.exc import SQLAlchemyError



# ============================================================================
# POSITIVE TEST CASES
# ============================================================================
fake = Faker()

def test_get_family_success(client, mock_db_session, sample_family_data, sample_user_data):
    """
    Test successful family retrieval.
    
    KEY POINTS:
    - Mocks database query to return family with users
    - Family route expects users relationship to be populated
    """
    # Arrange
    mock_family = Mock()
    mock_family.public_id = sample_family_data["public_id"]
    mock_family.name = sample_family_data["name"]  # ← Explicit string
    mock_family.created_at = datetime.fromisoformat(sample_family_data["created_at"])
    mock_family.updated_at = datetime.fromisoformat(sample_family_data["updated_at"])
    mock_family.id = fake.random_int(min=1, max=999999)
    

    mock_user = Mock()
    mock_user.public_id = sample_user_data["public_id"]
    mock_user.name = sample_user_data["name"]  # ← Explicit string
    mock_user.email = sample_user_data["email"]
    mock_user.username = sample_user_data.get("username", sample_user_data["name"])
    mock_user.role = UserRole.member
    mock_family.users = [mock_user]
    mock_user.is_active = True 
    
    # Configure the mock to return the family
    # query_mock = mock_db_session.query.return_value
    # query_mock.options.return_value = query_mock 
    # query_mock.filter.return_value.first.return_value = mock_family

    query_mock = mock_db_session.query.return_value
    query_mock.options.return_value.filter.return_value.first.return_value = mock_family
    family_id = sample_family_data["public_id"]
    # Act
    response = client.get(f"/api/v1/families/{family_id}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == sample_family_data["name"]


def test_get_family_tasks_success(client, mock_db_session, sample_family_data, sample_task_data):
    """
    Test successful family tasks retrieval.
    
    KEY POINTS:
    - Mocks database query for tasks on a specific date
    - Date parameter is passed as query string
    """
    # Arrange
    family_id = sample_family_data["public_id"]
    
    mock_family = Mock(**sample_family_data)
    query_mock = mock_db_session.query.return_value
    query_mock.options.return_value.filter.return_value.first.return_value = mock_family
    
    # Then mock tasks
    mock_tasks = [Mock(**sample_task_data)]
    query_mock.filter.return_value.all.return_value = mock_tasks

    test_date = datetime.now(timezone.utc).date().isoformat()
    mock_tasks = [Mock(**sample_task_data)]
    
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = mock_tasks
    
    # Act
    response = client.get(
        f"/api/v1/families/{family_id}/tasks",
        params={"date": test_date}
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


# ============================================================================
# NEGATIVE TEST CASES
# ============================================================================


def test_get_nonexistent_family(client, mock_db_session):
    """Test retrieving a family that doesn't exist."""
    # Arrange
    query_mock = mock_db_session.query.return_value
    query_mock.options.return_value = query_mock
    query_mock.filter.return_value.first.return_value = None
    
    # Act
    response = client.get("/api/v1/families/nonexistent-id")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_family_tasks_invalid_date(client, mock_db_session, sample_family_data):
    """Test retrieving family tasks with invalid date format."""
    # Arrange
    family_id = sample_family_data["public_id"]
    
    mock_family = Mock()
    mock_family.id = fake.random_int(min=1, max=999999)
    mock_family.public_id = family_id
    mock_family.name = "Test Family"
    mock_family.created_at = datetime.now(timezone.utc)
    mock_family.updated_at = datetime.now(timezone.utc)
    mock_family.users = []
    
    query_mock = mock_db_session.query.return_value
    query_mock.options.return_value.filter.return_value.first.return_value = mock_family
    # Act
    response = client.get(
        f"/api/v1/families/{family_id}/tasks",
        params={"date": "invalid-date"}
    )
    
    # Assert: Should return 422 for invalid date format
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_family_invalid_uuid(client):
    """Test retrieving a family with invalid UUID format."""
    # Act
    response = client.get("/api/v1/families/not-a-uuid")
    
    # Assert: Could be 404 or 422 depending on validation
    assert response.status_code in [
        status.HTTP_404_NOT_FOUND,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]


def test_get_family_database_error(client, mock_db_session, sample_family_data):
    """Test family retrieval when database query fails."""
    # Arrange: Configure mock to raise an exception
    query_mock = mock_db_session.query.return_value
    query_mock.options.return_value.filter.return_value.first.side_effect = Exception("Database error")
    
    response = client.get(f"/api/v1/families/{sample_family_data['public_id']}")
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# ============================================================================
# EDGE CASES
# ============================================================================


def test_get_family_no_members(client, mock_db_session, sample_family_data):
    """Test retrieving a family with no members."""
    # Arrange
    family_id = sample_family_data["public_id"]
    mock_family = Mock(
    public_id=sample_family_data["public_id"],
    name=sample_family_data["name"],
    created_at=datetime.fromisoformat(sample_family_data["created_at"]),
    updated_at=datetime.fromisoformat(sample_family_data["updated_at"]),
    id=sample_family_data.get("id", 1),
    users=[]  # Empty list
)
    
    # Explicitly set each attribute from sample_family_data
    for key, value in sample_family_data.items():
        setattr(mock_family, key, value)
    mock_family.users = []  # Empty users list

    query_mock = mock_db_session.query.return_value
    query_mock.options.return_value = query_mock 
    query_mock.filter.return_value.first.return_value = mock_family
    
    # Act
    response = client.get(f"/api/v1/families/{family_id}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    # Response should still contain family info even without members


def test_get_family_tasks_empty_result(client, mock_db_session, sample_family_data,  mock_family_factory):
    """Test retrieving family tasks when no tasks exist for the date."""
    # Arrange
    family_id = sample_family_data["public_id"]
    test_date = datetime.now(timezone.utc).date().isoformat()

    # Create mock family using the factory
    mock_family = mock_family_factory(
        public_id=family_id,
        name=sample_family_data["name"],
        users=[]
    )
    
    # Configure the query mock for this specific test
    # The query mock is already created in conftest, we just configure its behavior
    query_mock = mock_db_session.query.return_value
    
    # CRITICAL: Use side_effect to handle multiple queries
    # First call (.first()) returns the family
    # Second call (.all()) returns empty task list
    query_mock.first.side_effect = [mock_family]  # First query: get_family_by_id
    query_mock.all.side_effect = [[]] 


    # Act
    response = client.get(
        f"/api/v1/families/{family_id}/tasks",
        params={"date": test_date}
    )

    if response.status_code != 200:
        print(f"\n❌ Status Code: {response.status_code}")
        print(f"❌ Response Body: {response.json()}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_family_tasks_future_date(client, mock_db_session, sample_family_data, mock_family_factory):
    """Test retrieving family tasks for a future date."""
    # Arrange
    family_id = sample_family_data["public_id"]
    future_date = (datetime.now(timezone.utc).date().replace(year=2026)).isoformat()


    mock_family = mock_family_factory(
        public_id=family_id,
        name=sample_family_data["name"]
    )
    
    # Configure query mock
    query_mock = mock_db_session.query.return_value
    
    # CRITICAL: Configure for BOTH queries in your controller
    query_mock.first.side_effect = [mock_family]  # First query: get_family_by_id
    query_mock.all.side_effect = [[]] 
    
    # Act
    response = client.get(
        f"/api/v1/families/{family_id}/tasks",
        params={"date": future_date}
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK


def test_get_family_tasks_past_date(client, mock_db_session, sample_family_data,mock_family_factory):
    """Test retrieving family tasks for a past date."""
    # Arrange
    family_id = sample_family_data["public_id"]
    past_date = (datetime.now(timezone.utc).date().replace(year=2020)).isoformat()
    

    mock_family = mock_family_factory(public_id=family_id)
    
    # Configure query mock
    query_mock = mock_db_session.query.return_value
    query_mock.first.side_effect = [mock_family]  # Family lookup succeeds
    query_mock.all.side_effect = [[]]  # No tasks in past
    
    # Act
    response = client.get(
        f"/api/v1/families/{family_id}/tasks",
        params={"date": past_date}
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK


def test_get_family_with_large_member_count(client, mock_db_session, sample_family_data, sample_user_data,mock_family_factory, mock_user_factory):
    """Test retrieving a family with many members."""
  
    # Create 50 mock users
    family_id = sample_family_data["public_id"]
    family_db_id = sample_family_data["id"] 
    
    # ✅ Use the factory from conftest.py - that's what it's there for!
    mock_users = [
        mock_user_factory(family_id=family_id)  # Factory handles all the defaults
        for _ in range(50)
    ]
    
    # ✅ Use family factory too
    mock_family = mock_family_factory(
        id=family_db_id,
        public_id=family_id,
        name=sample_family_data["name"],
        users=mock_users
    )
    
    # Configure query mock properly
    query_mock = mock_db_session.query.return_value
    query_mock.options.return_value = query_mock
    query_mock.filter.return_value = query_mock
    query_mock.first.return_value = mock_family
    
    # Act
    response = client.get(f"/api/v1/families/{family_id}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == family_db_id  
    assert data["name"] == sample_family_data["name"]
    assert len(data["users"]) == 50


def test_create_family_member_database_error(
    client, mock_db_session, sample_user_data
):
    """Test family member creation when database fails - FIXED."""
    # Arrange
    
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value = query_mock
    
    # Make first query raise database error
    query_mock.first.side_effect = SQLAlchemyError("Database connection failed")
    
    # Act
    response = client.post(
        "/api/v1/users/new",
        json={
            "email": sample_user_data["email"],
            "name": sample_user_data["name"],
            "family_name": sample_user_data["family_name"],
            "family_id": sample_user_data["family_id"]
        }
    )
    
    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

# ============================================================================
# PERFORMANCE/STRESS TESTS
# ============================================================================


@pytest.mark.benchmark
def test_family_retrieval_performance(benchmark, client, mock_db_session, benchmark_user_data, mock_user_factory, mock_family_factory ):
    """Benchmark family data retrieval performance."""
    # Arrange
    family_id = "test-family-id"
    family_db_id = 12345 
    
    # Create 100 mock users
    mock_users = [
        mock_user_factory(family_id=family_id)
        for _ in range(100)
    ]
    
    # Create mock family
    mock_family = mock_family_factory(
        id=family_db_id, 
        public_id=family_id,
        name="Test Family",
        users=mock_users
    )
    
    # Configure query mock
    query_mock = mock_db_session.query.return_value
    query_mock.options.return_value = query_mock
    query_mock.filter.return_value = query_mock
    query_mock.first.return_value = mock_family

    response = client.get(f"/api/v1/families/{family_id}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == family_db_id
    # assert data["public_id"] == family_id
    assert len(data["users"]) == 100


@pytest.mark.benchmark
def test_family_tasks_retrieval_performance(benchmark, client, mock_db_session, benchmark_task_data):
    """Benchmark family tasks retrieval performance."""
    # Arrange
    family_id = "test-family-id"
    test_date = datetime.now(timezone.utc).date().isoformat()
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value  = benchmark_task_data
    
    def run_tasks_retrieval():
        client.get(
            f"/api/v1/families/{family_id}/tasks",
            params={"date": test_date}
        )
    
    result = benchmark(run_tasks_retrieval)
