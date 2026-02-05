"""
Content Generation Agent
Handles text and image generation tasks
"""
from crewai import Agent
from src.core.tools import TextGenerationTool, ImageGenerationTool


class ContentGenerationAgent:
    """Agent responsible for creating marketing content (text and images)"""
    
    def __init__(self):
        pass
    
    def create(self, llm) -> Agent:
        """
        Create content generation agent
        
        Args:
            llm: Language model for the agent
            
        Returns:
            CrewAI Agent configured for content generation
        """
        return Agent(
            role='Creative Content Specialist',
            goal='Generate high-quality marketing copy and visual assets.',
            backstory=(
                "You are a versatile creative professional capable of writing compelling copy "
                "and visualizing stunning imagery. You execute the plans provided by the strategist."
            ),
            tools=[TextGenerationTool(), ImageGenerationTool()],
            verbose=True,
            allow_delegation=False,
            llm=llm,
            function_calling_llm=llm
        )
