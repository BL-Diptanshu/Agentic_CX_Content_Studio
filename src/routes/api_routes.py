from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from src.core.database import get_db
from src.core.models import Campaign, TextContent, ImageContent
from src.core.text_content_gen import get_text_generator
from src.core.brand_validator import get_brand_validator, ValidationResult
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)
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
        logger.debug("Health check passed")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.post("/start_campaign")
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating campaign: {campaign.campaign_name} for brand: {campaign.brand}")
    try:
        new_campaign = Campaign(
            campaign_name=campaign.campaign_name,
            brand=campaign.brand,
            objective=campaign.objective,
            inputs=campaign.inputs
        )
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)
        logger.info(f"Campaign created successfully: ID={new_campaign.campaign_id}")
        return {"status": "created", "campaign_id": new_campaign.campaign_id, "data": new_campaign}
    except Exception as e:
        logger.error(f"Failed to create campaign: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

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

# Text Generation Endpoints
class TextGenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7

class TextGenerateResponse(BaseModel):
    generated_text: str
    model: str
    timestamp: str
    prompt: str

@router.post("/generate/text", response_model=TextGenerateResponse)
def generate_text(request: TextGenerateRequest):
    """
    Generate text using Groq API with Llama 3.1.
    """
    try:
        generator = get_text_generator()
        generated = generator.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return TextGenerateResponse(
            generated_text=generated,
            model=generator.model_name,
            timestamp=datetime.now().isoformat(),
            prompt=request.prompt
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")


class MarketingCopyRequest(BaseModel):
    campaign_name: str
    brand: str
    objective: str
    target_audience: Optional[str] = None
    max_tokens: Optional[int] = 200

@router.post("/generate/marketing-copy", response_model=TextGenerateResponse)
def generate_marketing_copy(request: MarketingCopyRequest):
    """
    Generate marketing copy for a campaign using Groq API.
    """
    try:
        generator = get_text_generator()
        generated = generator.generate_marketing_copy(
            campaign_name=request.campaign_name,
            brand=request.brand,
            objective=request.objective,
            target_audience=request.target_audience,
            max_tokens=request.max_tokens
        )
        
        return TextGenerateResponse(
            generated_text=generated,
            model=generator.model_name,
            timestamp=datetime.now().isoformat(),
            prompt=f"{request.campaign_name} - {request.brand}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Marketing copy generation failed: {str(e)}")

class ImageGenerateRequest(BaseModel):
    prompt: str
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    seed: Optional[int] = None

class ImageGenerateResponse(BaseModel):
    image_url: str
    model: str
    timestamp: str
    prompt: str

@router.post("/generate/image", response_model=ImageGenerateResponse)
def generate_image(request: ImageGenerateRequest):
    """
    Generate image using Replicate API with FLUX.1-dev.
    """
    try:
        from src.core.image_content_gen import ImageGenerator
        
        generator = ImageGenerator()
        image_url = generator.generate(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            seed=request.seed
        )
        
        return ImageGenerateResponse(
            image_url=image_url,
            model=generator.model,
            timestamp=datetime.now().isoformat(),
            prompt=request.prompt
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# Brand Validation Endpoints

class ValidateTextRequest(BaseModel):
    text: str
    strict: Optional[bool] = False

class ValidateTextResponse(BaseModel):
    is_valid: bool
    violations: list
    warnings: list
    detected_tone: str
    missing_keywords: list
    forbidden_words_found: list

@router.post("/validate/text", response_model=ValidateTextResponse)
def validate_text(request: ValidateTextRequest):
    """
    Validate text content against brand guidelines.
    
    Checks for:
    - Forbidden words
    - Required keywords
    - Tone consistency
    """
    try:
        validator = get_brand_validator(
            forbidden_words=["cheap", "scam", "fraud", "terrible", "worst", "hate"],
            required_keywords=["innovation", "quality", "premium"] if request.strict else []
        )
        
        result = validator.validate(request.text)
        
        return ValidateTextResponse(**result.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

class TextGenerateWithValidationResponse(BaseModel):
    generated_text: str
    model: str
    timestamp: str
    prompt: str
    validation: Optional[ValidateTextResponse] = None

@router.post("/generate/text-validated", response_model=TextGenerateWithValidationResponse)
def generate_text_with_validation(request: TextGenerateRequest):
    """
    Generate text and automatically validate against brand guidelines.
    """
    try:
        # Generate text
        generator = get_text_generator()
        generated = generator.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Validate generated text
        validator = get_brand_validator(
            forbidden_words=["cheap", "scam", "fraud", "terrible", "worst", "hate"],
            required_keywords=[]
        )
        validation_result = validator.validate(generated)
        
        return TextGenerateWithValidationResponse(
            generated_text=generated,
            model=generator.model_name,
            timestamp=datetime.now().isoformat(),
            prompt=request.prompt,
            validation=ValidateTextResponse(**validation_result.to_dict())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation with validation failed: {str(e)}")

@router.post("/generate/marketing-copy-validated", response_model=TextGenerateWithValidationResponse)
def generate_marketing_copy_with_validation(request: MarketingCopyRequest):
    """
    Generate marketing copy and automatically validate against brand guidelines.
    """
    try:
        # Generate marketing copy
        generator = get_text_generator()
        generated = generator.generate_marketing_copy(
            campaign_name=request.campaign_name,
            brand=request.brand,
            objective=request.objective,
            target_audience=request.target_audience,
            max_tokens=request.max_tokens
        )
        
        # Validate generated copy
        validator = get_brand_validator(
            forbidden_words=["cheap", "scam", "fraud", "terrible", "worst", "hate"],
            required_keywords=["innovation", "quality"]
        )
        validation_result = validator.validate(generated)
        
        return TextGenerateWithValidationResponse(
            generated_text=generated,
            model=generator.model_name,
            timestamp=datetime.now().isoformat(),
            prompt=f"{request.campaign_name} - {request.brand}",
            validation=ValidateTextResponse(**validation_result.to_dict())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Marketing copy generation with validation failed: {str(e)}")

def _save_orchestration_results(campaign_id: int, result_str: str, db: Session):
    """Helper to parse and save orchestration results"""
    try:
        # Simple heuristic to extract image URL (supports Replicate/generic URLs)
        # Looking for http/https in the string that looks like an image URL 
        # or just taking known patterns if available.
        # For now, regex for http(s)
        
        image_url = None
        text_content = result_str
        
        # Regex to find a URL
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, result_str)
        
        if urls:
            # Assume the last URL is the image if multiple? Or checking extension?
            # Replicate URLs usually are distinct.
            # For this MVP, let's take the first found URL as image if it looks like one, 
            # or just assume the tool puts it there.
            
            # Refined strategy: Just take the first URL
            image_url = urls[0]
        
        # Save Text
        text_entry = TextContent(
            campaign_id=campaign_id,
            generated_text=text_content,
            agent_name="ContentOrchestrationCrew",
            validation_status="COMPLETED" # Assumed validated by crew
        )
        db.add(text_entry)
        
        # Save Image if found
        if image_url:
            image_entry = ImageContent(
                campaign_id=campaign_id,
                generated_image_url=image_url,
                agent_name="ContentOrchestrationCrew",
                validation_status="COMPLETED"
            )
            db.add(image_entry)
            
        db.commit()
        return text_entry, image_url
        
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        # Don't raise, just log, so we return the result at least
        return None, None

@router.post("/orchestrate/campaign")
def orchestrate_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """
    Orchestrate a full campaign generation pipeline using CrewAI:
    Planning -> Content Generation -> Brand Validation.
    """
    try:
        from src.core.orchestrator import ContentOrchestrationCrew
        
        # 1. Create Campaign in DB first
        new_campaign = Campaign(
            campaign_name=campaign.campaign_name,
            brand=campaign.brand,
            objective=campaign.objective,
            inputs=campaign.inputs
        )
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)
        
        # 2. Run Crew
        # Convert Pydantic model to dict for CrewAI
        inputs = {
            "campaign_name": campaign.campaign_name,
            "brand": campaign.brand,
            "objective": campaign.objective or "Promote the brand",
            "inputs": campaign.inputs
        }
        
        orchestrator = ContentOrchestrationCrew()
        result = orchestrator.run_campaign(inputs)
        result_str = str(result)
        
        # 3. Save Results
        _save_orchestration_results(new_campaign.campaign_id, result_str, db)
        
        return {
            "status": "completed", 
            "campaign_id": new_campaign.campaign_id,
            "result": result_str
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

class RegenerationRequest(BaseModel):
    campaign_id: int
    feedback: Optional[str] = None

@router.post("/regenerate")
def regenerate_content(request: RegenerationRequest, db: Session = Depends(get_db)):
    """
    Regenerate content for an existing campaign.
    Retries the orchestration with the same inputs (plus feedback if supported later).
    """
    try:
        from src.core.orchestrator import ContentOrchestrationCrew
        
        # 1. Fetch Campaign
        campaign = db.query(Campaign).filter(Campaign.campaign_id == request.campaign_id).first()
        if not campaign:
             raise HTTPException(status_code=404, detail="Campaign not found")
        
        inputs = {
            "campaign_name": campaign.campaign_name,
            "brand": campaign.brand,
            "objective": campaign.objective or "Promote the brand",
            "inputs": campaign.inputs
        }
        
        # Add feedback to inputs if provided (Crew might need update to handle this, 
        # but passing it doesn't hurt)
        if request.feedback:
            inputs["feedback"] = request.feedback
            
        # 2. Re-run Crew
        orchestrator = ContentOrchestrationCrew()
        result = orchestrator.run_campaign(inputs)
        result_str = str(result)
        
        # 3. Save New Results
        _save_orchestration_results(campaign.campaign_id, result_str, db)
        
        return {
            "status": "regenerated",
            "campaign_id": campaign.campaign_id,
            "result": result_str
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {str(e)}")

class CampaignResultResponse(BaseModel):
    campaign_id: int
    campaign_name: str
    generated_text: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime

@router.get("/campaigns/{campaign_id}/results", response_model=CampaignResultResponse)
def get_campaign_results(campaign_id: int, db: Session = Depends(get_db)):
    """
    Get the latest generated results (text and image) for a campaign.
    """
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    # Get latest text content
    text_content = db.query(TextContent)\
        .filter(TextContent.campaign_id == campaign_id)\
        .order_by(TextContent.created_at.desc())\
        .first()
        
    # Get latest image content
    image_content = db.query(ImageContent)\
        .filter(ImageContent.campaign_id == campaign_id)\
        .order_by(ImageContent.created_at.desc())\
        .first()
        
    return CampaignResultResponse(
        campaign_id=campaign.campaign_id,
        campaign_name=campaign.campaign_name,
        generated_text=text_content.generated_text if text_content else None,
        image_url=image_content.generated_image_url if image_content else None,
        created_at=campaign.created_at
    )
