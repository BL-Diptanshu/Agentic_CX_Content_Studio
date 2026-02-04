import os
import replicate
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

class ImageGenerator:
    """
    Generates images using the Replicate API with the FLUX.1 models.
    """
    def __init__(self, model="black-forest-labs/flux-dev"):
        load_dotenv(override=True)
        
        self.model = model
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables.")

    def generate(self, prompt: str, width: int = 1024, height: int = 1024, seed: int = None) -> str:
        """
        Generates an image URL for the given prompt using Replicate.
        
        Args:
            prompt: The text prompt for image generation.
            width: Width of the image (supported by Flux, ignores if aspect_ratio is strictly used).
            height: Height of the image.
            seed: Optional integer for reproducibility.
            
        Returns:
            str: The URL to the generated image.
        """
        
        input_params = {
            "prompt": prompt,
            "go_fast": True, 
            "guidance": 3.5,
            "output_format": "webp",
            "output_quality": 90,
        }
        
        if seed is not None:
            input_params["seed"] = seed

        try:
            output = replicate.run(
                self.model,
                input=input_params
            )
            if isinstance(output, list) and len(output) > 0:
                logger.info(f"Image generated successfully: {output[0]}")
                return str(output[0])
            else:
                raise ValueError("Replicate returned empty output.")
                
        except Exception as e:
            logger.error(f"Error generating image with Replicate: {e}")
            raise

if __name__ == "__main__":
    try:
        gen = ImageGenerator()
        print("Generator initialized.")
    except Exception as e:
        print(f"Setup Error: {e}")

