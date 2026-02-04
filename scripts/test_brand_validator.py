"""
Test script for Brand Validator
Tests rule-based validation functionality
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.brand_validator import BrandValidator, ToneType


def test_brand_validator():
    """Test brand validator with various scenarios"""
    print("\n" + "="*80)
    print("Testing Brand Validator (User Story 5 - ML Engineer 1)")
    print("="*80)
    
    # Initialize validator with custom rules
    validator = BrandValidator(
        forbidden_words=["cheap", "scam", "terrible", "worst"],
        required_keywords=["quality", "premium"]
    )
    
    test_cases = [
        {
            "name": "Valid text with required keywords",
            "text": "Our premium quality products deliver excellence.",
            "expected_valid": True
        },
        {
            "name": "Text with forbidden word",
            "text": "This is the worst product ever, a total scam!",
            "expected_valid": False
        },
        {
            "name": "Text missing required keywords",
            "text": "Great products for everyday use.",
            "expected_valid": True  # Only warnings, not invalid
        },
        {
            "name": "Empty text",
            "text": "",
            "expected_valid": False
        },
        {
            "name": "Formal tone text",
            "text": "Furthermore, our quality solutions provide premium value. Moreover, excellence is guaranteed.",
            "expected_valid": True
        },
        {
            "name": "Casual tone text",
            "text": "Hey guys! This is pretty cool and awesome!",
            "expected_valid": True
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Text: '{test['text'][:50]}{'...' if len(test['text']) > 50 else ''}'")
        
        result = validator.validate(test['text'])
        
        print(f"  ✓ Valid: {result.is_valid}")
        print(f"  ✓ Tone: {result.detected_tone.value}")
        
        if result.violations:
            print(f"  ✗ Violations: {result.violations}")
        if result.warnings:
            print(f"  ⚠ Warnings: {result.warnings}")
        if result.forbidden_words_found:
            print(f"  ✗ Forbidden words: {result.forbidden_words_found}")
        if result.missing_keywords:
            print(f"  ⚠ Missing keywords: {result.missing_keywords}")
        
        # Check if test passed
        if result.is_valid == test['expected_valid']:
            print(f"  ✓ TEST PASSED")
            passed += 1
        else:
            print(f"  ✗ TEST FAILED (expected valid={test['expected_valid']}, got {result.is_valid})")
            failed += 1
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*80)
    
    return failed == 0


def test_validation_result_dict():
    """Test ValidationResult to_dict conversion"""
    print("\nTesting ValidationResult.to_dict()...")
    
    validator = BrandValidator()
    result = validator.validate("Test quality premium text")
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict), "Result should convert to dict"
    assert "is_valid" in result_dict, "Should have is_valid key"
    assert "detected_tone" in result_dict, "Should have detected_tone key"
    
    print("✓ ValidationResult.to_dict() works correctly")
    return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("BRAND VALIDATOR TEST SUITE")
    print("="*80)
    
    test1_passed = test_brand_validator()
    test2_passed = test_validation_result_dict()
    
    if test1_passed and test2_passed:
        print("\n✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)
