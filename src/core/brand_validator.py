"""
Brand Validator Module - KB Integrated
Provides rule-based brand validation using brand_kb/ knowledge base
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
    Rule-based brand validator using brand_kb/ knowledge base.
    Loads rules dynamically from JSON files.
    """
    
    def __init__(self, kb_path: str = "brand_kb"):
        """Initialize validator with KB rules"""
        from src.core.brand_kb_loader import get_kb_loader
        
        self.kb_loader = get_kb_loader(kb_path)
        
        # Load all KB rules
        self.forbidden_lang = self.kb_loader.load_forbidden_language()
        self.all_forbidden_terms = self.kb_loader.get_all_forbidden_terms()
        self.allowed_lang = self.kb_loader.load_allowed_language()
        self.all_allowed_phrases = self.kb_loader.get_all_allowed_phrases()
        self.tone_profile = self.kb_loader.load_tone_profile()
        
        # Tone detection patterns
        self.tone_patterns = {
            "fear-driven": ["afraid", "scared", "terrified", "panic", "disaster"],
            "aggressive": ["must", "have to", "obligated", "force", "demand"],
            "judgmental": ["should have", "failure", "wrong choice", "mistake"],
            "empathetic": ["understand", "support", "care", "help", "together"],
            "supportive": ["encourage", "assist", "guide", "empower"],
            "inclusive": ["everyone", "all", "inclusive", "accessible", "welcome"]
        }
        
        logger.info(
            f"BrandValidator initialized: {len(self.all_forbidden_terms)} forbidden terms, "
            f"{len(self.all_allowed_phrases)} allowed phrases"
        )
    
    def validate(self, text: str) -> ValidationResult:
        """Validate text against brand KB rules"""
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
        forbidden_found = []
        
        # Check forbidden language by category
        for category, terms in self.forbidden_lang.items():
            found = self._check_forbidden_category(text_lower, terms)
            if found:
                forbidden_found.extend(found)
                violations.append(
                    f"Contains {category.replace('_', ' ')}: {', '.join(found)}"
                )
        
        # Check tone violations
        tone_violations = self._check_disallowed_tones(text_lower)
        violations.extend(tone_violations)
        
        # Check for encouraged language
        encouraged = self._check_allowed_language(text_lower)
        if encouraged:
            warnings.append(f"✓ Good use of: {', '.join(encouraged)}")
        
        # Detect tone
        detected_tone = self._detect_dominant_tone(text_lower)
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            detected_tone=detected_tone,
            missing_keywords=[],
            forbidden_words_found=forbidden_found
        )
    
    def _check_forbidden_category(self, text: str, terms: List[str]) -> List[str]:
        """Check for forbidden terms"""
        return [term for term in terms if term.lower() in text]
    
    def _check_disallowed_tones(self, text: str) -> List[str]:
        """Check for disallowed tone indicators"""
        disallowed = self.tone_profile.get("disallowed_tone", [])
        violations = []
        
        for tone in disallowed:
            if tone in self.tone_patterns:
                found = [w for w in self.tone_patterns[tone] if w in text]
                if found:
                    violations.append(
                        f"Disallowed tone ({tone}): {', '.join(found[:2])}"
                    )
        
        return violations
    
    def _check_allowed_language(self, text: str) -> List[str]:
        """Find encouraged phrases"""
        found = []
        for phrases in self.allowed_lang.values():
            for phrase in phrases:
                if phrase.lower() in text:
                    found.append(phrase)
        return found
    
    def _detect_dominant_tone(self, text: str) -> ToneType:
        """Detect overall tone"""
        positive = sum(
            sum(1 for w in self.tone_patterns.get(t, []) if w in text)
            for t in ["empathetic", "supportive", "inclusive"]
        )
        negative = sum(
            sum(1 for w in self.tone_patterns.get(t, []) if w in text)
            for t in ["fear-driven", "aggressive", "judgmental"]
        )
        
        if positive > negative and positive > 0:
            return ToneType.FORMAL
        elif negative > 0:
            return ToneType.CASUAL
        return ToneType.NEUTRAL


_brand_validator: Optional[BrandValidator] = None


def get_brand_validator(kb_path: str = "brand_kb") -> BrandValidator:
    """Get global BrandValidator instance"""
    global _brand_validator
    if _brand_validator is None:
        _brand_validator = BrandValidator(kb_path)
    return _brand_validator
