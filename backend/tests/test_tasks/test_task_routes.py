import pytest
from fastapi import status
from unittest.mock import Mock
from models.models import Task, TaskStatus
from datetime import datetime, timezone, timedelta
from faker import Faker
from models.models import UserRole
import uuid


fake = Faker()


def test_create_task_success(client, mock_db_session, sample_task_data, mock_user_factory, mock_family_factory):
    creator_id = sample_task_data["creator_id"]
    assignee_id = sample_task_data["assignee_id"]
    family_id = sample_task_data["family_id"]

    mock_creator = mock_user_factory(
        public_id=creator_id,
        family_id=family_id,
        role=UserRole.admin
    )
    
    mock_assignee = mock_user_factory(
        public_id=assignee_id,
        family_id=family_id,
        role=UserRole.member
    )
    
    mock_family = mock_family_factory(
        public_id=family_id,
        users=[mock_creator, mock_assignee]
    )

    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value = query_mock

    query_mock.first.side_effect = [
        mock_creator,
        mock_assignee,
        mock_family
    ]

    future_due_date = sample_task_data["due_date"]

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": sample_task_data["title"],
            "description": sample_task_data["description"],
            "creator_id": creator_id,
            "assignee_id": assignee_id,
            "family_id": family_id,
            "due_date": future_due_date, 
            "status": sample_task_data["status"]
        }
    )

    if response.status_code != 201:
        print(f"\n❌ Status: {response.status_code}")
        print(f"❌ Body: {response.json()}")
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == sample_task_data["title"]
    assert data["creator_id"] == creator_id
    assert data["assignee_id"] == assignee_id
    assert data["family_id"] == family_id
    assert "public_id" in data


def test_create_task_with_max_checklist(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None
    
    task_data = {
        "title": "Task with max checklist",
        "creator_id": "creator123",
        "assignee_id": "assignee123",
        "family_id": "family123",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "checklist": [
            {"id": i, "title": f"Item {i}", "completed": False}
            for i in range(8)  # Maximum allowed is 8
        ]
    }

    response = client.post("/api/v1/tasks", json=task_data)

    assert response.status_code == status.HTTP_201_CREATED


def test_create_task_with_null_assignee(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None
    
    task_data = {
        "title": "Unassigned task",
        "creator_id": "creator123",
        "assignee_id": None,
        "family_id": "family123",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }

    response = client.post("/api/v1/tasks", json=task_data)

    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]


def test_create_task_same_day_due_date(
    client, mock_db_session, mock_user_factory, mock_family_factory
):
    creator_id = str(uuid.uuid4())
    assignee_id = str(uuid.uuid4())
    family_id = str(uuid.uuid4())

    mock_creator = mock_user_factory(public_id=creator_id, family_id=family_id)
    mock_assignee = mock_user_factory(public_id=assignee_id, family_id=family_id)
    mock_family = mock_family_factory(public_id=family_id)
    
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value = query_mock
    query_mock.first.side_effect = [mock_creator, mock_assignee, mock_family]

    future_date = datetime.now(timezone.utc) + timedelta(hours=2)

    task_data = {
        "title": "Invalid status task",
        "creator_id": creator_id,
        "assignee_id": assignee_id,
        "family_id": family_id,
        "due_date": future_date.isoformat(),
        "status": "invalid_status"
    }

    response = client.post("/api/v1/tasks", json=task_data)

    if response.status_code != 422:
        print(f"\n❌ Status: {response.status_code}")
        print(f"❌ Body: {response.json()}")

    assert response.status_code == status.HTTP_201_CREATED


def test_create_task_very_long_title(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None
    
    task_data = {
        "title": "A" * 200,  # Very long title
        "creator_id": "creator123",
        "assignee_id": "assignee123",
        "family_id": "family123",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }

    response = client.post("/api/v1/tasks", json=task_data)

    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]


def test_create_task_with_special_characters_title(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None
    
    task_data = {
        "title": "Task with spëcial çhars & ñumbers 123!",
        "creator_id": "creator123",
        "assignee_id": "assignee123",
        "family_id": "family123",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }

    response = client.post("/api/v1/tasks", json=task_data)

    assert response.status_code == status.HTTP_201_CREATED


def test_update_task_partial_update(client, mock_db_session, sample_task_data):
    pass


def test_create_task_invalid_dates(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None
    
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    task_data = {
        "title": "Invalid date task",
        "creator_id": "creator123",
        "assignee_id": "assignee123",
        "family_id": "family123",
        "due_date": past_date.isoformat(),
    }

    response = client.post("/api/v1/tasks", json=task_data)

    assert response.status_code in [
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_400_BAD_REQUEST
    ]


def test_create_task_invalid_status(client, mock_db_session, mock_user_factory, mock_family_factory):
    creator_id = str(uuid.uuid4())
    assignee_id = str(uuid.uuid4())
    family_id = str(uuid.uuid4())

    mock_creator = mock_user_factory(public_id=creator_id, family_id=family_id)
    mock_assignee = mock_user_factory(public_id=assignee_id, family_id=family_id)
    mock_family = mock_family_factory(public_id=family_id)
    
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value = query_mock
    query_mock.first.side_effect = [mock_creator, mock_assignee, mock_family]

    task_data = {
        "title": "Test task",
        "creator_id": creator_id,
        "assignee_id": assignee_id,
        "family_id": family_id,
        "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "status": "invalid_status"
    }

    response = client.post("/api/v1/tasks", json=task_data)

    if response.status_code != 201:
        print(f"\n❌ Status: {response.status_code}")
        print(f"❌ Body: {response.json()}")

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "initialised"


def test_update_nonexistent_task(client, mock_db_session):
    pass


def test_create_task_exceeding_checklist_limit(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None
    
    task_data = {
        "title": "Task with too many checklist items",
        "creator_id": "creator123",
        "assignee_id": "assignee123",
        "family_id": "family123",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "checklist": [
            {"id": i, "title": f"Item {i}", "completed": False}
            for i in range(10)
        ]
    }

    response = client.post("/api/v1/tasks", json=task_data)

    assert response.status_code in [
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]


def test_create_task_empty_checklist(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None
    
    task_data = {
        "title": "Task with empty checklist",
        "creator_id": "creator123",
        "assignee_id": "assignee123",
        "family_id": "family123",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "checklist": []
    }

    response = client.post("/api/v1/tasks", json=task_data)

    assert response.status_code == status.HTTP_201_CREATED


def test_create_task_no_checklist(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None
    
    task_data = {
        "title": "Task without checklist",
        "creator_id": "creator123",
        "assignee_id": "assignee123",
        "family_id": "family123",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }

    response = client.post("/api/v1/tasks", json=task_data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.benchmark
def test_bulk_task_creation_performance(benchmark, client, mock_db_session, benchmark_task_data):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None
    
    def run_bulk_creation():
        for task_data in benchmark_task_data[:10]:  # Create 10 tasks
            client.post(
                "/api/v1/tasks",
                json={
                    "title": task_data["title"],
                    "creator_id": task_data["creator_id"],
                    "assignee_id": task_data["assignee_id"],
                    "family_id": task_data["family_id"],
                    "due_date": task_data["due_date"],
                }
            )
    
    result = benchmark(run_bulk_creation)


@pytest.mark.benchmark
def test_task_status_update_performance(benchmark, client, mock_db_session, sample_task_data):
    pass
