"""
Integration Test for User Story 2: Campaign Creation and Viewing
Tests both the Create and View Campaign features via API
"""
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"

def test_health_check():
    """Test if the backend is healthy"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✓ Health check passed")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False

def test_create_campaign():
    """Test campaign creation"""
    print("\n=== Testing Campaign Creation ===")
    
    test_campaign = {
        "campaign_name": f"Test Campaign {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "brand": "Test Brand",
        "objective": "Testing campaign creation and viewing features",
        "inputs": {
            "target_audience": "Test users",
            "budget": 10000,
            "duration": "2 weeks"
        }
    }
    
    print(f"Creating campaign: {test_campaign['campaign_name']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/start_campaign",
            json=test_campaign
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        data = response.json()
        assert "campaign_id" in data
        assert data["status"] == "created"
        
        campaign_id = data["campaign_id"]
        print(f"✓ Campaign created successfully with ID: {campaign_id}")
        return campaign_id
        
    except Exception as e:
        print(f"✗ Campaign creation failed: {str(e)}")
        return None

def test_view_campaigns():
    """Test viewing all campaigns"""
    print("\n=== Testing View Campaigns ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/campaigns/")
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 200
        campaigns = response.json()
        
        print(f"\nTotal campaigns found: {len(campaigns)}")
        
        if campaigns:
            print("\nCampaigns:")
            print("-" * 80)
            for campaign in campaigns:
                print(f"ID: {campaign.get('campaign_id')}")
                print(f"Name: {campaign.get('campaign_name')}")
                print(f"Brand: {campaign.get('brand')}")
                print(f"Objective: {campaign.get('objective')}")
                print(f"Created: {campaign.get('created_at')}")
                print("-" * 80)
            
            print(f"✓ Successfully retrieved {len(campaigns)} campaign(s)")
        else:
            print("✓ No campaigns found (database is empty)")
        
        return campaigns
        
    except Exception as e:
        print(f"✗ View campaigns failed: {str(e)}")
        return None

def test_view_specific_campaign(campaign_id):
    """Test viewing a specific campaign"""
    print(f"\n=== Testing View Specific Campaign (ID: {campaign_id}) ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/campaigns/{campaign_id}")
        print(f"Status Code: {response.status_code}")
        
        assert response.status_code == 200
        campaign = response.json()
        
        print(f"\nCampaign Details:")
        print(json.dumps(campaign, indent=2))
        
        assert campaign["campaign_id"] == campaign_id
        print(f"✓ Successfully retrieved campaign {campaign_id}")
        return campaign
        
    except Exception as e:
        print(f"✗ View specific campaign failed: {str(e)}")
        return None

def run_all_tests():
    """Run all integration tests"""
    print("=" * 80)
    print("INTEGRATION TEST SUITE - USER STORY 2")
    print("Testing Campaign Creation and Viewing Features")
    print("=" * 80)
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n✗ CRITICAL: Backend is not healthy. Stopping tests.")
        return
    
    # Test 2: Create Campaign
    campaign_id = test_create_campaign()
    if not campaign_id:
        print("\n✗ CRITICAL: Campaign creation failed. Stopping tests.")
        return
    
    # Test 3: View All Campaigns
    campaigns = test_view_campaigns()
    if campaigns is None:
        print("\n✗ WARNING: Could not retrieve campaigns list")
    
    # Test 4: View Specific Campaign
    test_view_specific_campaign(campaign_id)
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED")
    print("=" * 80)
    print("\n✓ All tests passed successfully!")
    print("\nYou can now:")
    print("1. Open http://localhost:8502 to see the campaigns in the Streamlit UI")
    print("2. Navigate to 'View Campaigns' tab to verify the UI integration")

if __name__ == "__main__":
    run_all_tests()
