"""
Quick test for brand_kb integration
"""
import sys
sys.path.insert(0, '.')
from src.core.brand_validator import get_brand_validator

# Initialize validator
validator = get_brand_validator()

# Test cases
test_cases = [
    "Guaranteed 100% success with instant results!",
    "Designed to support your journey with care and empathy.",
    "Act now or regret this last chance forever!",
    "Our solution is clinically proven to be a medical cure."
]

print("=" * 60)
print("Brand KB Validation Tests")
print("=" * 60)

for i, text in enumerate(test_cases, 1):
    print(f"\nTest {i}: \"{text}\"")
    result = validator.validate(text)
    
    print(f"Valid: {result.is_valid}")
    if result.violations:
        print(f"Violations:")
        for v in result.violations:
            print(f"  - {v}")
    if result.warnings:
        print(f"Warnings:")
        for w in result.warnings:
            print(f"  - {w}")
    print(f"Tone: {result.detected_tone.value}")

print("\n" + "=" * 60)
