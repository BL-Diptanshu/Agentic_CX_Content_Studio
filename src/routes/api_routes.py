from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.core.database import get_db
from src.core.models import Campaign, TextContent
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()

class CampaignCreate(BaseModel):
    campaign_name: str
    brand: str
    objective: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.post("/campaigns/")
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    new_campaign = Campaign(
        campaign_name=campaign.campaign_name,
        brand=campaign.brand,
        objective=campaign.objective,
        inputs=campaign.inputs
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return {"status": "created", "campaign_id": new_campaign.campaign_id, "data": new_campaign}

@router.get("/campaigns/")
def list_campaigns(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    return campaigns

@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

class TextContentCreate(BaseModel):
    campaign_id: int
    generated_text: str
    prompt_used: Optional[str] = None
    agent_name: str = "The Writer"
    validation_status: str = "PENDING"

@router.post("/contents/text")
def create_text_content(content: TextContentCreate, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.campaign_id == content.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    new_content = TextContent(
        campaign_id=content.campaign_id,
        generated_text=content.generated_text,
        prompt_used=content.prompt_used,
        agent_name=content.agent_name,
        validation_status=content.validation_status
    )
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content

