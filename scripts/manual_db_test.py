import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    print("Starting Manual End-to-End Test...")

    # 1. Create Campaign
    print("\n[1] Creating Campaign...")
    payload = {
        "campaign_name": "Test Campaign 1",
        "brand": "Acme Corp",
        "objective": "Brand Awareness",
        "inputs": {"target_audience": "Tech enthusiasts"}
    }
    try:
        response = requests.post(f"{BASE_URL}/campaigns/", json=payload)
        response.raise_for_status()
        data = response.json()
        campaign_id = data["campaign_id"]
        print(f"Success! Campaign ID: {campaign_id}")
        print(f"Response: {data}")
    except Exception as e:
        print(f"Failed to create campaign: {e}")
        return

    # 2. Add Text Content
    print("\n[2] Adding Text Content...")
    content_payload = {
        "campaign_id": campaign_id,
        "generated_text": "Welcome to the future of AI.",
        "prompt_used": "Write a futuristic slogan",
        "agent_name": "Writer Agent",
        "validation_status": "approved"
    }
    try:
        response = requests.post(f"{BASE_URL}/contents/text", json=content_payload)
        response.raise_for_status()
        print(f"Success! Content Added: {response.json()}")
    except Exception as e:
        print(f"Failed to add content: {e}")
        return

    # 3. Retrieve Campaign
    print(f"\n[3] Retrieving Campaign {campaign_id}...")
    try:
        response = requests.get(f"{BASE_URL}/campaigns/{campaign_id}")
        response.raise_for_status()
        print(f"Success! Retrieved Campaign: {response.json()}")
    except Exception as e:
        print(f"Failed to get campaign: {e}")

    print("\n✅ End-to-End Test Completed.")

if __name__ == "__main__":
    # Ensure server is running before running this
    run_test()
