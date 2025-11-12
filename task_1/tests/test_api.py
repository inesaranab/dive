"""Tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db_session
from app.models import Base


# Create test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data
    assert "categories" in data


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_classify_technology():
    """Test classification of a technology article."""
    response = client.post(
        "/classify",
        json={
            "message": "Apple announces new iPhone with advanced AI features and improved camera system."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_label" in data
    assert "predicted_category" in data
    assert data["predicted_label"] in [0, 1, 2, 3, 4]
    assert isinstance(data["predicted_category"], str)


def test_classify_sport():
    """Test classification of a sports article."""
    response = client.post(
        "/classify",
        json={
            "message": "Manchester United defeats Liverpool 3-1 in the Premier League match today."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_label" in data
    assert "predicted_category" in data


def test_classify_invalid_input():
    """Test classification with invalid input."""
    response = client.post("/classify", json={"message": ""})
    assert response.status_code == 422  # Validation error


def test_get_history():
    """Test retrieving classification history."""
    # First, make a classification
    client.post(
        "/classify",
        json={"message": "Test article about business and economy."},
    )

    # Then retrieve history
    response = client.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "records" in data
    assert isinstance(data["records"], list)


def test_get_history_pagination():
    """Test history pagination."""
    response = client.get("/history?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "records" in data
    assert len(data["records"]) <= 10

