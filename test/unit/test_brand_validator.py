"""
Unit tests for Brand Validator
Tests BrandValidator class validation logic
"""
import pytest
from unittest.mock import patch, MagicMock
from src.core.brand_validator import (
    BrandValidator,
    ValidationResult,
    ToneType,
    get_brand_validator
)


@pytest.fixture
def mock_kb_loader():
    """Mock KB loader for testing"""
    mock_loader = MagicMock()
    
    # Mock forbidden language
    mock_loader.load_forbidden_language.return_value = {
        "inappropriate": ["cheap", "discount", "sale"],
        "fear_based": ["afraid", "scared", "panic"]
    }
    mock_loader.get_all_forbidden_terms.return_value = ["cheap", "discount", "sale", "afraid", "scared", "panic"]
    
    # Mock allowed language
    mock_loader.load_allowed_language.return_value = {
        "empowering": ["empower", "achieve", "greatness"],
        "inclusive": ["everyone", "all", "together"]
    }
    mock_loader.get_all_allowed_phrases.return_value = ["empower", "achieve", "greatness", "everyone", "all", "together"]
    
    # Mock tone profile
    mock_loader.load_tone_profile.return_value = {
        "disallowed_tone": ["fear-driven", "aggressive"],
        "preferred_tone": ["empathetic", "supportive"]
    }
    
    return mock_loader


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_validator_initialization(mock_get_kb, mock_kb_loader):
    """Test BrandValidator initializes correctly"""
    mock_get_kb.return_value = mock_kb_loader
    
    validator = BrandValidator(kb_path="test_kb")
    
    assert validator.kb_loader is not None
    assert len(validator.all_forbidden_terms) > 0
    assert len(validator.all_allowed_phrases) > 0


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_validate_clean_text(mock_get_kb, mock_kb_loader):
    """Test validation of clean text with no violations"""
    mock_get_kb.return_value = mock_kb_loader
    validator = BrandValidator()
    
    text = "Together we can achieve greatness and empower everyone"
    result = validator.validate(text)
    
    assert isinstance(result, ValidationResult)
    assert result.is_valid is True
    assert len(result.violations) == 0


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_validate_forbidden_words(mock_get_kb, mock_kb_loader):
    """Test detection of forbidden words"""
    mock_get_kb.return_value = mock_kb_loader
    validator = BrandValidator()
    
    text = "Get this cheap product on sale with a discount"
    result = validator.validate(text)
    
    assert result.is_valid is False
    assert len(result.forbidden_words_found) > 0
    assert "cheap" in result.forbidden_words_found


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_validate_empty_text(mock_get_kb, mock_kb_loader):
    """Test validation of empty text"""
    mock_get_kb.return_value = mock_kb_loader
    validator = BrandValidator()
    
    result = validator.validate("")
    
    assert result.is_valid is False
    assert "Text is empty" in result.violations
    assert result.detected_tone == ToneType.UNKNOWN


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_detect_positive_tone(mock_get_kb, mock_kb_loader):
    """Test detection of positive/empathetic tone"""
    mock_get_kb.return_value = mock_kb_loader
    validator = BrandValidator()
    
    text = "We understand your needs and want to help support you together"
    result = validator.validate(text)
    
    # Should detect formal/positive tone
    assert result.detected_tone in [ToneType.FORMAL, ToneType.NEUTRAL]


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_detect_negative_tone(mock_get_kb, mock_kb_loader):
    """Test detection of negative/aggressive tone"""
    mock_get_kb.return_value = mock_kb_loader
    validator = BrandValidator()
    
    text = "You must do this now or face disaster and panic"
    result = validator.validate(text)
    
    # Should detect violations from disallowed tones
    assert len(result.violations) > 0


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_case_insensitive_detection(mock_get_kb, mock_kb_loader):
    """Test forbidden words detection is case-insensitive"""
    mock_get_kb.return_value = mock_kb_loader
    validator = BrandValidator()
    
    text = "This is CHEAP and on SALE"
    result = validator.validate(text)
    
    assert "cheap" in result.forbidden_words_found or "sale" in result.forbidden_words_found


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_validation_result_to_dict(mock_get_kb, mock_kb_loader):
    """Test ValidationResult conversion to dictionary"""
    result = ValidationResult(
        is_valid=True,
        violations=[],
        warnings=["Good use of empowering language"],
        detected_tone=ToneType.FORMAL,
        missing_keywords=[],
        forbidden_words_found=[]
    )
    
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict)
    assert result_dict["is_valid"] is True
    assert result_dict["detected_tone"] == "formal"
    assert len(result_dict["warnings"]) > 0


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_get_brand_validator_singleton(mock_get_kb, mock_kb_loader):
    """Test get_brand_validator returns singleton"""
    mock_get_kb.return_value = mock_kb_loader
    
    val1 = get_brand_validator()
    val2 = get_brand_validator()
    
    # Should return same instance
    assert val1 is val2


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_multiple_violations(mock_get_kb, mock_kb_loader):
    """Test text with multiple violations"""
    mock_get_kb.return_value = mock_kb_loader
    validator = BrandValidator()
    
    text = "Cheap sale discount afraid panic scared"
    result = validator.validate(text)
    
    assert result.is_valid is False
    assert len(result.forbidden_words_found) >= 2
    assert len(result.violations) >= 1


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_whitespace_only_text(mock_get_kb, mock_kb_loader):
    """Test validation of whitespace-only text"""
    mock_get_kb.return_value = mock_kb_loader
    validator = BrandValidator()
    
    result = validator.validate("   \n\t  ")
    
    assert result.is_valid is False
    assert result.detected_tone == ToneType.UNKNOWN


@patch("src.core.brand_kb_loader.get_kb_loader")
def test_allowed_language_detection(mock_get_kb, mock_kb_loader):
    """Test detection of encouraged language"""
    mock_get_kb.return_value = mock_kb_loader
    validator = BrandValidator()
    
    text = "We empower everyone to achieve greatness together"
    result = validator.validate(text)
    
    # Should have positive warnings about good language use
    assert result.is_valid is True
    # Warnings might contain encouragement messages
    assert len(result.violations) == 0
