"""
Complete Fixed Auth Tests - Big Tech Pattern
All tests use persistent mock pattern with proper Redis/Celery mocking
"""

import pytest
from fastapi import status
from unittest.mock import Mock, patch 
import json
from datetime import datetime, timezone
from utils.error_handler import AppError, ErrorCode


# ============================================================================
# POSITIVE TEST CASES - SIGNUP
# ============================================================================


def test_signup_success(client, mock_db_session, mock_redis, sample_user_data):
    """Test successful user signup."""
    # Configure persistent query mock
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.first.return_value = None
    
    signup_data = {
        "email": sample_user_data["email"],
        "password": "StrongP@ssw0rd123!",
        "name": sample_user_data["name"],
        "family_name": sample_user_data["family_name"]
    }
    
    response = client.post("/api/v1/auth/signup", json=signup_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == signup_data["email"]
    assert "user_id" in data
    assert data["requires_verification"] is True


def test_signup_invalid_email(client, sample_user_data):
    """Test signup with invalid email format."""
    signup_data = {
        "email": "not-an-email",
        "password": "StrongP@ssw0rd123!",
        "name": sample_user_data["name"],
        "family_name": sample_user_data["family_name"]
    }
    
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_missing_required_fields(client):
    """Test signup with missing required fields."""
    signup_data = {"email": "test@example.com"}
    
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# NEGATIVE TEST CASES - SIGNUP
# ============================================================================


def test_signup_existing_email(client, mock_db_session, sample_user_data):
    """Test signup with an existing email."""
    existing_user = Mock(email=sample_user_data["email"])
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.first.return_value = existing_user
    
    signup_data = {
        "email": sample_user_data["email"],
        "password": "StrongP@ssw0rd123!",
        "name": sample_user_data["name"],
        "family_name": sample_user_data["family_name"]
    }
    
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_signup_database_failure(client, mock_db_session, sample_user_data):
    """Test signup when database fails during user creation."""
    mock_db_session.flush.side_effect = Exception("Database error")
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.first.return_value = None
    
    signup_data = {
        "email": sample_user_data["email"],
        "password": "StrongP@ssw0rd123!",
        "name": sample_user_data["name"],
        "family_name": sample_user_data["family_name"]
    }
    
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_signup_weak_password(client, mock_db_session, sample_user_data):
    """Test signup with weak password."""
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.first.return_value = None
    
    # FIX: Mock Auth0 to reject weak password
    with patch("controllers.auth_controller.create_auth0_user") as mock_auth0:
        mock_auth0.side_effect = AppError(
            code=ErrorCode.BAD_REQUEST,
            status_code=400,
            technical_message="Password too weak",
            user_message="Password does not meet requirements",
            is_operational=True,
            details={}
        )
        
        signup_data = {
            "email": sample_user_data["email"],
            "password": "weak",
            "name": sample_user_data["name"],
            "family_name": sample_user_data["family_name"]
        }
        
        response = client.post("/api/v1/auth/signup", json=signup_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# EDGE CASES - SIGNUP
# ============================================================================


def test_signup_very_long_email(client, mock_db_session):
    """Test signup with very long email address."""
    long_email = "a" * 250 + "@example.com"
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.first.return_value = None
    
    signup_data = {
        "email": long_email,
        "password": "StrongP@ssw0rd123!",
        "name": "John Doe",
        "family_name": "Doe"
    }
    
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]


def test_signup_special_characters_in_name(client, mock_db_session):
    """Test signup with special characters in name."""
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.first.return_value = None
    
    signup_data = {
        "email": "test@example.com",
        "password": "StrongP@ssw0rd123!",
        "name": "José María O'Connor",
        "family_name": "Pérez-López"
    }
    
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_signup_email_case_insensitive(client, mock_db_session, sample_user_data):
    """Test that email comparison is case-insensitive."""
    existing_user = Mock(email=sample_user_data["email"].lower())
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.first.return_value = existing_user
    
    signup_data = {
        "email": sample_user_data["email"].upper(),  # Different case
        "password": "StrongP@ssw0rd123!",
        "name": sample_user_data["name"],
        "family_name": sample_user_data["family_name"]
    }
    
    response = client.post("/api/v1/auth/signup", json=signup_data)
    # Should detect duplicate regardless of case
    assert response.status_code == status.HTTP_409_CONFLICT


# ============================================================================
# IDEMPOTENCY TESTS
# ============================================================================



def test_signup_with_idempotency_hit(client, mock_redis, sample_user_data):
    """Test that idempotency key returns cached response."""
    idempotency_key = "test-idempotency-key"
    cached_response = {
        "message": "User created successfully",
        "user_id": "cached-user-id",
        "email": sample_user_data["email"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requires_verification": True
    }
    
    # Configure Redis mock to return cached response
    mock_redis._test_cache[f"idempotency:{idempotency_key}"] = json.dumps(cached_response)

    
    signup_data = {
        "email": sample_user_data["email"],
        "password": "StrongP@ssw0rd123!",
        "name": sample_user_data["name"],
        "family_name": sample_user_data["family_name"]
    }
    
    response = client.post(
        "/api/v1/auth/signup",
        json=signup_data,
        headers={"Idempotency-Key": idempotency_key}
    )
    
    assert response.status_code == status.HTTP_201_CREATED


def test_signup_without_idempotency_key(client, mock_db_session, sample_user_data):
    """Test signup without idempotency key still works."""
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.first.return_value = None
    
    signup_data = {
        "email": sample_user_data["email"],
        "password": "StrongP@ssw0rd123!",
        "name": sample_user_data["name"],
        "family_name": sample_user_data["family_name"]
    }
    
    # No idempotency header
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == status.HTTP_201_CREATED


# ============================================================================
# PERFORMANCE/STRESS TESTS
# ============================================================================


@pytest.mark.benchmark
def test_signup_performance(benchmark, client, mock_db_session):
    """Benchmark signup endpoint performance."""
    query_mock = mock_db_session.query.return_value
    query_mock.filter.return_value.first.return_value = None
    
    def run_signup():
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "perf_test@example.com",
                "password": "StrongP@ssw0rd123!",
                "name": "Performance",
                "family_name": "Test"
            }
        )
        return response.status_code == status.HTTP_201_CREATED
    
    result = benchmark(run_signup)
    assert result is True