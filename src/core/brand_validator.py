"""
Brand Validator Module
Provides rule-based brand validation for content (forbidden words, required keywords, tone checking).
"""
import re
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ToneType(Enum):
    """Enum for tone classification"""
    FORMAL = "formal"
    CASUAL = "casual"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    """Result of brand validation check"""
    is_valid: bool
    violations: List[str]
    warnings: List[str]
    detected_tone: ToneType
    missing_keywords: List[str]
    forbidden_words_found: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            "is_valid": self.is_valid,
            "violations": self.violations,
            "warnings": self.warnings,
            "detected_tone": self.detected_tone.value,
            "missing_keywords": self.missing_keywords,
            "forbidden_words_found": self.forbidden_words_found
        }


class BrandValidator:
    """
    Rule-based brand validator that checks text against brand guidelines.
    
    Validates:
    - Forbidden words/phrases (banned terms)
    - Required keywords (brand terms that should be present)
    - Tone (formal vs casual language patterns)
    """
    
    def __init__(
        self,
        forbidden_words: Optional[List[str]] = None,
        required_keywords: Optional[List[str]] = None,
        formal_indicators: Optional[List[str]] = None,
        casual_indicators: Optional[List[str]] = None
    ):
        """
        Initialize brand validator with rule sets.
        
        Args:
            forbidden_words: List of banned terms/phrases
            required_keywords: List of required brand keywords
            formal_indicators: Words/patterns indicating formal tone
            casual_indicators: Words/patterns indicating casual tone
        """
        # Default forbidden words (common inappropriate terms)
        self.forbidden_words: Set[str] = set(forbidden_words or [
            "cheap", "scam", "fraud", "terrible", "worst", "hate"
        ])
        
        # Default required keywords (should be customized per brand)
        self.required_keywords: Set[str] = set(required_keywords or [])
        
        # Tone indicators
        self.formal_indicators: Set[str] = set(formal_indicators or [
            "furthermore", "therefore", "moreover", "consequently", 
            "nevertheless", "accordingly", "henceforth"
        ])
        
        self.casual_indicators: Set[str] = set(casual_indicators or [
            "hey", "cool", "awesome", "yeah", "gonna", "wanna", 
            "kinda", "pretty much", "you guys"
        ])
        
        logger.info("BrandValidator initialized with %d forbidden words, %d required keywords",
                   len(self.forbidden_words), len(self.required_keywords))
    
    def validate(self, text: str) -> ValidationResult:
        """
        Validate text against all brand rules.
        
        Args:
            text: Content text to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        if not text or not text.strip():
            return ValidationResult(
                is_valid=False,
                violations=["Text is empty"],
                warnings=[],
                detected_tone=ToneType.UNKNOWN,
                missing_keywords=[],
                forbidden_words_found=[]
            )
        
        text_lower = text.lower()
        violations = []
        warnings = []
        
        # Check forbidden words
        forbidden_found = self.check_forbidden_words(text_lower)
        if forbidden_found:
            violations.append(f"Contains forbidden words: {', '.join(forbidden_found)}")
        
        # Check required keywords
        missing_kw = self.check_required_keywords(text_lower)
        if missing_kw:
            warnings.append(f"Missing required keywords: {', '.join(missing_kw)}")
        
        # Check tone
        detected_tone = self.check_tone(text_lower)
        
        # Determine if valid (no violations)
        is_valid = len(violations) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            detected_tone=detected_tone,
            missing_keywords=missing_kw,
            forbidden_words_found=forbidden_found
        )
    
    def check_forbidden_words(self, text: str) -> List[str]:
        """
        Check for forbidden words in text.
        
        Args:
            text: Lowercase text to check
            
        Returns:
            List of forbidden words found
        """
        found = []
        for word in self.forbidden_words:
            # Use word boundaries to match whole words
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found.append(word)
        return found
    
    def check_required_keywords(self, text: str) -> List[str]:
        """
        Check for required keywords in text.
        
        Args:
            text: Lowercase text to check
            
        Returns:
            List of missing required keywords
        """
        missing = []
        for keyword in self.required_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if not re.search(pattern, text, re.IGNORECASE):
                missing.append(keyword)
        return missing
    
    def check_tone(self, text: str) -> ToneType:
        """
        Detect tone of text based on indicator words.
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            Detected ToneType
        """
        formal_count = sum(1 for word in self.formal_indicators if word in text)
        casual_count = sum(1 for word in self.casual_indicators if word in text)
        
        if formal_count == 0 and casual_count == 0:
            return ToneType.NEUTRAL
        elif formal_count > casual_count:
            return ToneType.FORMAL
        elif casual_count > formal_count:
            return ToneType.CASUAL
        else:
            return ToneType.NEUTRAL


# Singleton instance
_validator_instance: Optional[BrandValidator] = None


def get_brand_validator(
    forbidden_words: Optional[List[str]] = None,
    required_keywords: Optional[List[str]] = None
) -> BrandValidator:
    """
    Get or create singleton BrandValidator instance.
    
    Args:
        forbidden_words: Optional custom forbidden words list
        required_keywords: Optional custom required keywords list
        
    Returns:
        BrandValidator instance
    """
    global _validator_instance
    
    if _validator_instance is None:
        _validator_instance = BrandValidator(
            forbidden_words=forbidden_words,
            required_keywords=required_keywords
        )
    
    return _validator_instance
