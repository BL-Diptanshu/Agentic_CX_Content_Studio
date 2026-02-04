from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.core.database import get_db
from src.core.models import Campaign, TextContent
from src.core.text_content_gen import get_text_generator
from src.core.brand_validator import get_brand_validator, ValidationResult
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

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

@router.post("/start_campaign")
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
