import pytest
from fastapi import status
from unittest.mock import Mock
from controllers.user_controller import deactivate_user, reactivate_user
from models.models import UserRole
import uuid
from unittest.mock import patch
from utils.error_handler import AppError, ErrorCode



def test_create_family_member_success(client, mock_db_session, sample_user_data):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value = query_mock
    query_mock.first.return_value = None

    response = client.post(
        "/api/v1/users/new",
        json={
            "email": sample_user_data["email"],
            "name": sample_user_data["name"],
            "family_name": sample_user_data["family_name"],
            "family_id": sample_user_data["family_id"]
        }
    )
    
    # Debug output
    if response.status_code != 201:
        print(f"\n❌ Status: {response.status_code}")
        print(f"❌ Body: {response.json()}")

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == sample_user_data["email"]


def test_get_user_success(
    client, mock_db_session, sample_user_data, sample_family_data, mock_user_factory, mock_family_factory
):
    mock_user = mock_user_factory(
        id=sample_user_data["id"],
        public_id=sample_user_data["public_id"],
        email=sample_user_data["email"],
        name=sample_user_data["name"],
        family_name=sample_user_data["family_name"],
        family_id=sample_user_data["family_id"],
        username=sample_user_data["username"],
        role=UserRole.member,
        is_active=sample_user_data["is_active"]
    )
    
    mock_family = mock_family_factory(
        id=sample_family_data["id"],
        public_id=sample_family_data["public_id"],
        name=sample_family_data["name"]
    )

    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value = query_mock
    
    query_mock.first.side_effect = [mock_user, mock_family]
    query_mock.all.return_value = [mock_user]

    response = client.post(
        "/api/v1/users/me",
        json={"user_email": sample_user_data["email"]}
    )

    if response.status_code != 200:
        print(f"\n❌ Status: {response.status_code}")
        print(f"❌ Body: {response.json()}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == sample_user_data["email"]


def test_create_family_member_duplicate_email(
    client, mock_db_session, sample_user_data, mock_user_factory
):
    existing_user = mock_user_factory(
        email=sample_user_data["email"],
        name=sample_user_data["name"]
    )
    
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value = query_mock
    query_mock.first.return_value = existing_user

    response = client.post(
        "/api/v1/users/new",
        json={
            "email": sample_user_data["email"],
            "name": sample_user_data["name"],
            "family_name": sample_user_data["family_name"],
            "family_id": sample_user_data["family_id"]
        }
    )

    if response.status_code != 409:
        print(f"\n❌ Status: {response.status_code}")
        print(f"❌ Body: {response.json()}")

    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_user_not_found(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = None

    response = client.get("/api/v1/users/nonexistent@email.com")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_family_member_auth0_failure(client, mock_db_session, sample_user_data):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value = query_mock
    query_mock.first.return_value = None

    with patch("controllers.user_controller.create_auth0_user") as mock_auth0:
        async def auth0_failure(*args, **kwargs):
            raise AppError(
                code=ErrorCode.SERVICE_UNAVAILABLE,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                technical_message="Auth0 service unavailable",
                user_message="Unable to create user account",
                is_operational=True,
                details={}
            )
        
        mock_auth0.side_effect = auth0_failure

        response = client.post(
            "/api/v1/users/new",
            json={
                "email": sample_user_data["email"],
                "name": sample_user_data["name"],
                "family_name": sample_user_data["family_name"],
                "family_id": sample_user_data["family_id"]
            }
        )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_reactivate_inactive_user(client, mock_db_session, sample_user_data):
    user_id = sample_user_data["public_id"]
    mock_db_session.query().filter().update.return_value = 1

    response = client.patch(f"/api/v1/users/{user_id}/activate")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_db_session.commit.assert_called()


def test_deactivate_already_inactive_user(client, mock_db_session, sample_user_data):
    user_id = sample_user_data["public_id"]
    mock_db_session.query().filter().update.return_value = 1

    response = client.patch(f"/api/v1/users/{user_id}/deactivate")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_create_family_member_with_special_characters(client, mock_db_session):
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value = query_mock
    query_mock.first.return_value = None

    response = client.post(
        "/api/v1/users/new",
        json={
            "email": "test@example.com",
            "name": "José María O'Connor",
            "family_name": "Pérez-López",
            "family_id": str(uuid.uuid4())
        }
    )
    
    # Debug output
    if response.status_code != 201:
        print(f"\n❌ Status: {response.status_code}")
        print(f"❌ Body: {response.json()}")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.benchmark
def test_deactivate_user_performance(benchmark, client, mock_db_session, benchmark_user_data):
    mock_db_session.query().filter().update.return_value = 1
    
    def run_deactivation():
        user = benchmark_user_data[0]
        client.patch(f"/api/v1/users/{user['public_id']}/deactivate")
    
    result = benchmark(run_deactivation)


@pytest.mark.benchmark
def test_user_retrieval_performance(benchmark, client, mock_db_session, benchmark_user_data):
    mock_user = Mock(**benchmark_user_data[0])
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.all.return_value = mock_user
    
    def run_retrieval():
        user = benchmark_user_data[0]
        client.get(f"/api/v1/users/{user['email']}")
    
    result = benchmark(run_retrieval)
