from crewai import Agent
import os
from src.rag.brand_retriever import BrandGuidelineRetriever

class CampaignPlannerAgent:
    def __init__(self):
        pass

    def create(self, llm) -> Agent:
        return Agent(
            role='Campaign Planner',
            goal='Create detailed content briefs for marketing campaigns based on high-level objectives, strictly adhering to brand guidelines.',
            backstory=(
                "You are an expert marketing strategist with years of experience in digital campaigns. "
                "Your job is to take a campaign name, brand, and objective, and break it down into "
                "specific actionable tasks for content creators. You decide what text needs to be written "
                "and what images need to be generated to support the campaign goals. "
                "CRITICAL: You MUST use the Brand Guideline Retriever tool to check for brand voice, tone, "
                "and forbidden language before creating any plan. Your plans must explicitly reference "
                "these guidelines."
            ),
            tools=[BrandGuidelineRetriever()],
            allow_delegation=False,
            verbose=True,
            llm=llm,
            function_calling_llm=llm
        )
