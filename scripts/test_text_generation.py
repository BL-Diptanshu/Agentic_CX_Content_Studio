"""
Test script for Text Generation functionality using Groq API
Tests both the basic text generation and marketing copy generation endpoints
"""
import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test API health"""
    print("\n" + "="*80)
    print("Testing API Health")
    print("="*80)
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_basic_text_generation():
    """Test basic text generation endpoint with Groq"""
    print("\n" + "="*80)
    print("Testing Basic Text Generation (Groq Llama 3.1)")
    print("="*80)
    
    test_prompt = "Create a marketing campaign for summer sales"
    
    payload = {
        "prompt": test_prompt,
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    print(f"\nPrompt: {test_prompt}")
    print(f"Max Tokens: {payload['max_tokens']}")
    print(f"Temperature: {payload['temperature']}")
    
    try:
        print("\nCalling /generate/text endpoint...")
        response = requests.post(
            f"{API_BASE_URL}/generate/text",
            json=payload,
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nModel Used: {data['model']}")
            print(f"Timestamp: {data['timestamp']}")
            print(f"\nGenerated Text:")
            print("-" * 80)
            print(data['generated_text'])
            print("-" * 80)
            print("\n✓ Basic text generation successful!")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_marketing_copy_generation():
    """Test marketing copy generation endpoint with Groq"""
    print("\n" + "="*80)
    print("Testing Marketing Copy Generation (Groq Llama 3.1)")
    print("="*80)
    
    payload = {
        "campaign_name": "Summer Sale 2024",
        "brand": "TechStore",
        "objective": "Increase summer product sales by 30%",
        "target_audience": "Tech enthusiasts aged 25-40",
        "max_tokens": 200
    }
    
    print(f"\nCampaign: {payload['campaign_name']}")
    print(f"Brand: {payload['brand']}")
    print(f"Objective: {payload['objective']}")
    print(f"Target Audience: {payload['target_audience']}")
    
    try:
        print("\nCalling /generate/marketing-copy endpoint...")
        response = requests.post(
            f"{API_BASE_URL}/generate/marketing-copy",
            json=payload,
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nModel Used: {data['model']}")
            print(f"Timestamp: {data['timestamp']}")
            print(f"\nGenerated Marketing Copy:")
            print("-" * 80)
            print(data['generated_text'])
            print("-" * 80)
            print("\n✓ Marketing copy generation successful!")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def run_all_tests():
    """Run all text generation tests"""
    print("\n" + "="*80)
    print("TEXT GENERATION TEST SUITE - GROQ LLAMA 3.1")
    print("User Story 3 - ML Engineer 1")
    print("="*80)
    
    results = {
        "health": False,
        "basic_generation": False,
        "marketing_copy": False
    }
    
    # Test 1: Health Check
    results["health"] = test_health()
    if not results["health"]:
        print("\n✗ CRITICAL: API not healthy. Stopping tests.")
        return
    
    # Test 2: Basic Text Generation
    results["basic_generation"] = test_basic_text_generation()
    
    # Test 3: Marketing Copy Generation
    results["marketing_copy"] = test_marketing_copy_generation()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Health Check: {'✓ PASS' if results['health'] else '✗ FAIL'}")
    print(f"Basic Text Generation: {'✓ PASS' if results['basic_generation'] else '✗ FAIL'}")
    print(f"Marketing Copy Generation: {'✓ PASS' if results['marketing_copy'] else '✗ FAIL'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED!")
        print("\nGroq Llama 3.1 text generation is working correctly.")
        print("You can now use the endpoints in your application.")
    else:
        print("\n✗ SOME TESTS FAILED")
        print("Please check the errors above.")
    
    print("="*80)

if __name__ == "__main__":
    run_all_tests()
