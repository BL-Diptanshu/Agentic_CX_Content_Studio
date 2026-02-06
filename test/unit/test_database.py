
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.core.database import Base
from src.core.models import Campaign, TextContent, ImageContent

# Use in-memory SQLite with StaticPool for persistence across session creation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_db):
    session = TestingSessionLocal()
    yield session
    session.close()

def test_create_campaign(db_session):
    campaign = Campaign(
        campaign_name="Unit Test Campaign",
        brand="UnitBrand",
        objective="Testing",
        inputs={"audience": "Bots"}
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)
    
    assert campaign.campaign_id is not None
    assert campaign.campaign_name == "Unit Test Campaign"

def test_create_text_content(db_session):
    # Setup campaign
    campaign = Campaign(campaign_name="Content Test", brand="Brand", objective="Obj", inputs={})
    db_session.add(campaign)
    db_session.commit()
    
    # Create content
    text_content = TextContent(
        campaign_id=campaign.campaign_id,
        generated_text="Some generated content",
        agent_name="TestWriter",
        validation_status="PENDING"
    )
    db_session.add(text_content)
    db_session.commit()
    db_session.refresh(text_content)
    
    assert text_content.text_id is not None
    assert text_content.generated_text == "Some generated content"
    assert text_content.campaign_id == campaign.campaign_id

def test_cascade_delete_behavior(db_session):
    # This checks if we have defined cascade or if we need to manually clean up.
    # Currently models.py doesn't strictly define cascade='all, delete', but let's test behavior.
    
    campaign = Campaign(campaign_name="Delete Test", brand="Brand", objective="Obj", inputs={})
    db_session.add(campaign)
    db_session.commit()
    
    content = TextContent(campaign_id=campaign.campaign_id, generated_text="To be deleted", agent_name="Writer")
    db_session.add(content)
    db_session.commit()
    
    # Verify both exist
    assert db_session.query(Campaign).filter_by(campaign_id=campaign.campaign_id).count() == 1
    assert db_session.query(TextContent).filter_by(campaign_id=campaign.campaign_id).count() == 1
    
    # Delete campaign
    db_session.delete(campaign)
    db_session.commit()
    
    # Verify campaign is gone
    assert db_session.query(Campaign).filter_by(campaign_id=campaign.campaign_id).count() == 0
    # Note: SQLAlchemy default relationship without cascade usually sets FK to null or raises error if not nullable.
    # In models.py we just have ForeignKey. Let's see what happens.
    # If this fails, it's good finding for robustness.
