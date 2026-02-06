
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from src.core.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.core.models import Campaign

# Setup in-memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    yield db
    db.close()

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}

def test_create_campaign(client, db_session):
    payload = {
        "campaign_name": "API Test Campaign",
        "brand": "API Brand",
        "objective": "Test",
        "inputs": {"key": "value"}
    }
    response = client.post("/api/v1/start_campaign", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert "campaign_id" in data
    
    # Verify DB
    campaign_id = data["campaign_id"]
    campaign = db_session.query(Campaign).filter_by(campaign_id=campaign_id).first()
    assert campaign is not None
    assert campaign.campaign_name == "API Test Campaign"

def test_get_campaign_not_found(client):
    response = client.get("/api/v1/campaigns/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Campaign not found"

@patch("src.routes.api_routes.get_text_generator")
def test_generate_text_mocked(mock_get_gen, client):
    # Setup Mock
    mock_instance = MagicMock()
    mock_instance.generate_text.return_value = "Mocked Generated Text"
    mock_instance.model_name = "mock-model"
    mock_get_gen.return_value = mock_instance
    
    payload = {"prompt": "Test prompt", "max_tokens": 50}
    response = client.post("/api/v1/generate/text", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["generated_text"] == "Mocked Generated Text"
    assert data["model"] == "mock-model"

@patch("src.routes.api_routes.get_brand_validator")
def test_validate_text_mocked(mock_get_validator, client):
    # Setup Mock
    mock_instance = MagicMock()
    
    # Mock result object
    mock_result = MagicMock()
    mock_result.to_dict.return_value = {
        "is_valid": True,
        "violations": [],
        "warnings": [],
        "detected_tone": "neutral",
        "missing_keywords": [],
        "forbidden_words_found": []
    }
    mock_instance.validate.return_value = mock_result
    mock_get_validator.return_value = mock_instance
    
    payload = {"text": "Safe text content"}
    response = client.post("/api/v1/validate/text", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["detected_tone"] == "neutral"

@patch("src.core.orchestrator.ContentOrchestrationCrew")
def test_regenerate_endpoint(mock_crew_cls, client, db_session):
    # Setup - Create campaign data first
    campaign = Campaign(campaign_name="Regen API Test", brand="Brand", objective="Obj", inputs={})
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)
    
    # Setup Mock for Orchestrator
    mock_instance = MagicMock()
    mock_instance.run_campaign.return_value = "Regenerated content https://img.com/1.png"
    mock_crew_cls.return_value = mock_instance
    
    payload = {"campaign_id": campaign.campaign_id, "feedback": "Better"}
    response = client.post("/api/v1/regenerate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "regenerated"
    assert "https://img.com/1.png" in data["result"]

