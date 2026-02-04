"""
Text Content Generator Module
Uses Groq API with Llama 3.1 for text generation
"""
import os
from groq import Groq
import logging
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import mlflow
import time

logger = logging.getLogger(__name__)

class TextGenerator:
    """Text generation using Groq API with Llama 3.1"""
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """
        Initialize text generator with Groq API.
        
        Args:
            model_name: Groq model name (default: llama-3.1-8b-instant)
        """
        # Load environment variables fresh each time
        load_dotenv(override=True)
        
        self.model_name = model_name
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file.")
        
        self.client = Groq(api_key=api_key)
        
        # Initialize MLflow experiment
        try:
            experiment_name = "text_content_generation"
            mlflow.set_experiment(experiment_name)
            logger.info(f"MLflow experiment set to: {experiment_name}")
        except Exception as e:
            logger.warning(f"Failed to set MLflow experiment: {e}")

        logger.info(f"Initialized TextGenerator with Groq model: {model_name}")
    
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate text based on the given prompt using Groq API.
        
        Args:
            prompt: Input text to continue
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated text string
        """
        start_time = time.time()
        try:
            logger.info(f"Generating text for prompt: '{prompt[:50]}...'")
            
            with mlflow.start_run():
                # Log parameters
                mlflow.log_param("model_name", self.model_name)
                mlflow.log_param("max_tokens", max_tokens)
                mlflow.log_param("temperature", temperature)
                mlflow.log_param("top_p", top_p)
                
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                )
                
                generated_text = chat_completion.choices[0].message.content
                end_time = time.time()
                generation_time_ms = (end_time - start_time) * 1000
                
                # Log metrics and attributes
                mlflow.log_metric("generation_time_ms", generation_time_ms)
                mlflow.log_metric("input_length", len(prompt))
                mlflow.log_metric("output_length", len(generated_text))
                mlflow.set_tag("prompt_snippet", prompt[:100])
                
                logger.info(f"Successfully generated {len(generated_text)} characters in {generation_time_ms:.2f}ms")
                
                return generated_text
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise
    
    def generate_marketing_copy(
        self,
        campaign_name: str,
        brand: str,
        objective: str,
        target_audience: Optional[str] = None,
        max_tokens: int = 200
    ) -> str:
        """
        Generate marketing copy for a campaign.
        
        Args:
            campaign_name: Name of the campaign
            brand: Brand name
            objective: Campaign objective
            target_audience: Target audience description
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated marketing copy
        """
        
        prompt = f"""Write compelling marketing copy for {brand}'s '{campaign_name}' campaign.

Campaign Objective: {objective}
"""
        
        if target_audience:
            prompt += f"Target Audience: {target_audience}\n"
        
        prompt += "\nGenerate engaging marketing copy that captures attention and drives action:"
        
        return self.generate_text(prompt, max_tokens=max_tokens)


_text_generator_instance = None

def get_text_generator(model_name: str = "llama-3.1-8b-instant") -> TextGenerator:
    """
    Get or create singleton TextGenerator instance.
    
    Args:
        model_name: Groq model to use
        
    Returns:
        TextGenerator instance
    """
    global _text_generator_instance
    
    if _text_generator_instance is None:
        _text_generator_instance = TextGenerator(model_name)
    
    return _text_generator_instance
