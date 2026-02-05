import logging
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class RegenerationManager:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.forbidden_words = ["cheap", "scam", "fraud", "terrible", "worst", "hate"]
        self.required_keywords = ["innovation", "quality", "premium"]
    
    def run_with_regeneration(self, orchestrator, inputs: Dict[str, Any]) -> Dict[str, Any]:
        for attempt in range(self.max_retries):
            logger.info(f"Attempt {attempt + 1}/{self.max_retries}")
            
            result = orchestrator.run_campaign(inputs)
            
            validation_status = self.parse_validation_result(result)
            
            if validation_status == "APPROVED":
                logger.info("Content approved!")
                return {
                    "status": "success",
                    "attempts": attempt + 1,
                    "result": result
                }
            
            logger.warning(f"Validation failed on attempt {attempt + 1}")
            
            if attempt < self.max_retries - 1:
                inputs = self.enhance_prompt_for_retry(inputs, attempt)
        
        return {
            "status": "failed_after_retries",
            "attempts": self.max_retries,
            "result": result
        }
    
    def parse_validation_result(self, crew_output) -> str:
        result_str = str(crew_output).lower()
        
        if "rejected" in result_str or "invalid" in result_str or "failed" in result_str:
            return "REJECTED"
        
        if "approved" in result_str or "valid" in result_str:
            return "APPROVED"
        
        return "APPROVED"
    
    def enhance_prompt_for_retry(self, inputs: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        enhanced_inputs = inputs.copy()
        
        brand_emphasis = self._build_brand_emphasis(attempt)
        
        if "objective" in enhanced_inputs:
            enhanced_inputs["objective"] = f"{enhanced_inputs['objective']}\n\n{brand_emphasis}"
        else:
            enhanced_inputs["objective"] = brand_emphasis
        
        logger.info(f"Enhanced prompt for retry {attempt + 1}")
        return enhanced_inputs
    
    def _build_brand_emphasis(self, attempt: int) -> str:
        emphasis_levels = [
            f"IMPORTANT: Avoid these words: {', '.join(self.forbidden_words)}. Use these keywords: {', '.join(self.required_keywords)}.",
            f"CRITICAL: Content must NOT contain: {', '.join(self.forbidden_words)}. MUST include: {', '.join(self.required_keywords)}. Maintain professional, premium tone.",
            f"FINAL ATTEMPT: Strictly forbidden words: {', '.join(self.forbidden_words)}. Required keywords: {', '.join(self.required_keywords)}. Focus on quality, innovation, and premium positioning."
        ]
        
        return emphasis_levels[min(attempt, len(emphasis_levels) - 1)]


def run_campaign_with_regeneration(orchestrator, inputs: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
    manager = RegenerationManager(max_retries=max_retries)
    return manager.run_with_regeneration(orchestrator, inputs)
