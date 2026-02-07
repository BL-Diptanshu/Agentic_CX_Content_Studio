from crewai.tools import BaseTool
import json
from src.core.text_content_gen import get_text_generator

from src.core.brand_validator import get_brand_validator

class TextGenerationTool(BaseTool):
    name: str = "Text Generation Tool"
    description: str = (
        "Generates text content based on a prompt. "
        "Input should be a clear, detailed prompt describing what you want to write."
    )

    def _run(self, prompt: str) -> str:
        generator = get_text_generator()
        # Default parameters, can be adjusted if we expose them in inputs
        return generator.generate_text(prompt=prompt, max_tokens=500)

class ImageGenerationTool(BaseTool):
    name: str = "Image Generation Tool"
    description: str = (
        "Generates an image based on a prompt using Hugging Face Inference API. "
        "Input should be a detailed visual description of the desired image."
    )

    def _run(self, prompt: str) -> str:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"ImageGenerationTool called with prompt: {prompt}")
        from src.core.hf_image_gen import HuggingFaceGenerator
        generator = HuggingFaceGenerator()
        try:
            url = generator.generate(prompt=prompt)
            return f"Image generated successfully via HF. URL: {url}"
        except Exception as e:
            return f"Image generation failed: {str(e)}"

class BrandValidationTool(BaseTool):
    name: str = "Brand Content Validator"
    description: str = (
        "Validates if the content adheres to brand guidelines. "
        "Input should be the text content to check. "
        "Returns validation status and any violations."
    )

    def _run(self, content: str) -> str:
        validator = get_brand_validator(
            forbidden_words=["cheap", "scam", "fraud", "terrible", "worst", "hate"],
            required_keywords=["innovation", "quality", "premium"]
        )
        result = validator.validate(content)
        return json.dumps(result.to_dict(), indent=2)
