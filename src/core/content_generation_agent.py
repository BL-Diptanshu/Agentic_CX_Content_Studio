"""Content Generation Agent"""
from crewai import Agent
from src.core.tools import TextGenerationTool, ImageGenerationTool

class ContentGenerationAgent:
    def __init__(self):
        pass
    
    def create(self, llm) -> Agent:
        return Agent(
            role='Content Creator',
            goal='Generate copy and visuals.',
            backstory='Creative professional. Executes plans.',
            tools=[TextGenerationTool(), ImageGenerationTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            llm=llm
        )
