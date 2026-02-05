from crewai import Agent
from src.core.tools import BrandValidationTool

class BrandValidationAgent:
    def __init__(self):
        pass

    def create(self, llm) -> Agent:
        return Agent(
            role='Brand Compliance Officer',
            goal='Ensure all marketing content adheres strictly to brand guidelines.',
            backstory=(
                "You are the guardian of the brand's reputation. "
                "You review every piece of content meticulously to ensure it matches the brand voice, "
                "uses the correct terminology, and avoids any forbidden words."
            ),
            tools=[BrandValidationTool()],
            verbose=True,
            allow_delegation=False,
            llm=llm,
            function_calling_llm=llm
        )
