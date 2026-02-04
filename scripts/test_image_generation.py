"""
Test script for Image Generation (Replicate / Flux)
"""
import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.image_content_gen import ImageGenerator

def test_image_gen():
    print("🚀 Testing Image Generation (Replicate / Flux)...")
    print("-" * 50)
    
    try:
        # 1. Initialize
        print("Initializing Generator...")
        gen = ImageGenerator()
        print("✅ Initialization successful.")
        
        # 2. Generate
        prompt = "Futuristic city with flying cars at sunset, cyberpunk style, high detail."
        print(f"\n🎨 Generating image for prompt:\n'{prompt}'")
        print("\n(This may take 10-20 seconds)...")
        
        image_url = gen.generate(prompt)
        
        print("\n✅ Generation Successful!")
        print(f"🖼️  Image URL: {image_url}")
        print("-" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_image_gen()
