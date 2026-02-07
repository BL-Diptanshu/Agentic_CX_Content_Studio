"""Campaign Planning Agent"""
from crewai import Agent
from src.rag.brand_retriever import BrandGuidelineRetriever

class CampaignPlannerAgent:
    def __init__(self):
        pass
    
    def create(self, llm) -> Agent:
        return Agent(
            role='Campaign Strategist',
            goal='Create campaign plans aligned with brand.',
            backstory='Marketing strategist who uses brand guidelines.',
            tools=[],
            allow_delegation=False,
            verbose=True,
            llm=llm
        )
