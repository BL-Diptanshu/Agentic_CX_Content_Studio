
import os
import logging
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import time
import requests
from PIL import Image
import io

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class HuggingFaceGenerator:
    """
    Generates images using the Hugging Face Inference API (Free Tier).
    Uses 'stabilityai/stable-diffusion-xl-base-1.0' by default.
    """
    def __init__(self, model_id="stabilityai/stable-diffusion-xl-base-1.0"):
        self.model_id = model_id
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        
        if not self.api_token:
            logger.warning("HUGGINGFACE_API_TOKEN not found! Using anonymous access (might be rate limited).")
        
        self.client = InferenceClient(token=self.api_token)
        logger.info(f"Initialized HuggingFaceGenerator with model: {self.model_id}")

    def generate(self, prompt: str) -> str:
        """
        Generates an image from the prompt and saves it locally.
        Returns the local URL path.
        """
        try:
            logger.info(f"Generating image via Hugging Face: '{prompt}'...")
            start_time = time.time()
            
            # Use text_to_image specifically
            image = self.client.text_to_image(
                prompt,
                model=self.model_id
            )
            
            # Ensure static directory exists
            static_dir = os.path.join(os.getcwd(), "static", "generated")
            os.makedirs(static_dir, exist_ok=True)
            
            # Unique filename
            filename = f"img_hf_{int(time.time())}.png"
            full_path = os.path.join(static_dir, filename)
            
            image.save(full_path)
            
            elapsed = time.time() - start_time
            logger.info(f"Image saved to {full_path} in {elapsed:.2f}s")
            
            return f"/static/generated/{filename}"
            
        except Exception as e:
            logger.error(f"HF Image generation failed: {e}")
            raise

if __name__ == "__main__":
    # Test
    try:
        gen = HuggingFaceGenerator()
        print("Generator loaded.")
        path = gen.generate("A futuristic city optimized for wellness, 8k resolution")
        print(f"Generated: {path}")
    except Exception as e:
        print(f"Error: {e}")
