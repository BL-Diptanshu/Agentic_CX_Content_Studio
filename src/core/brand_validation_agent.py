"""Brand Validation Agent"""
from crewai import Agent

class BrandValidationAgent:
    def __init__(self):
        pass
    
    def create(self, llm) -> Agent:
        return Agent(
            role='Brand Validator',
            goal='Validate plans match brand guidelines.',
            backstory='Brand guardian. Validates by reading plan text.',
            tools=[],
            verbose=True,
            allow_delegation=False,
            allow_code_execution=False,
            llm=llm
        )
