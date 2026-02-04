import os
import replicate
import logging
from dotenv import load_dotenv
import mlflow
import time

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
        
        # Initialize MLflow experiment
        try:
            experiment_name = "image_content_generation"
            mlflow.set_experiment(experiment_name)
            logger.info(f"MLflow experiment set to: {experiment_name}")
        except Exception as e:
            logger.warning(f"Failed to set MLflow experiment: {e}")

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
        start_time = time.time()
        
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
            with mlflow.start_run():
                # Log parameters
                mlflow.log_param("model", self.model)
                mlflow.log_param("width", width)
                mlflow.log_param("height", height)
                mlflow.log_param("guidance", 3.5)
                mlflow.log_param("output_quality", 90)
                if seed is not None:
                    mlflow.log_param("seed", seed)

                output = replicate.run(
                    self.model,
                    input=input_params
                )
                
                end_time = time.time()
                generation_time_ms = (end_time - start_time) * 1000
                
                if isinstance(output, list) and len(output) > 0:
                    image_url = str(output[0])
                    # Log metrics and attributes
                    mlflow.log_metric("generation_time_ms", generation_time_ms)
                    mlflow.set_tag("prompt", prompt)
                    mlflow.set_tag("output_url", image_url)
                    
                    logger.info(f"Image generated successfully in {generation_time_ms:.2f}ms: {image_url}")
                    return image_url
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

