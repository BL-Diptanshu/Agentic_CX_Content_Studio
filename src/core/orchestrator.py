from crewai import Crew, Task, Agent
from langchain_groq import ChatGroq
import os
from src.core.campaign_planner_agent import CampaignPlannerAgent
from src.core.brand_validation_agent import BrandValidationAgent
from src.core.tools import TextGenerationTool, ImageGenerationTool

class ContentOrchestrationCrew:
    def __init__(self):
        # Force OpenAI compatibility layers to use Groq within this process context
        # This fixes issues where CrewAI/LiteLLM might fall back to default OpenAI client
        if os.getenv("GROQ_API_KEY"):
            os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
            os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"

        # Initialize Groq LLMs
        self.planning_llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.writing_llm = ChatGroq(
            model_name="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.planner_agent = CampaignPlannerAgent().create(llm=self.planning_llm)
        self.validator_agent = BrandValidationAgent().create(llm=self.planning_llm)
        
        # specialized agent for content creation
        self.content_agent = Agent(
            role='Creative Content Specialist',
            goal='Generate high-quality marketing copy and visual assets.',
            backstory=(
                "You are a versatile creative professional capable of writing compelling copy "
                "and visualizing stunning imagery. You execute the plans provided by the strategist."
            ),
            tools=[TextGenerationTool(), ImageGenerationTool()],
            verbose=True,
            allow_delegation=False,
            llm=self.writing_llm,
            function_calling_llm=self.writing_llm
        )

    def run_campaign(self, inputs: dict) -> dict:
        """
        Run the orchestration crew for a campaign.
        
        Args:
            inputs: Dict containing 'campaign_name', 'brand', 'objective', etc.
        """
        
        # Task 1: Plan the content
        planning_task = Task(
            description=(
                f"Analyze the campaign request for '{inputs.get('brand')}' campaign '{inputs.get('campaign_name')}'.\n"
                f"Objective: {inputs.get('objective')}\n"
                f"Create a detailed plan that specifies:\n"
                f"1. A specific text prompt for marketing copy.\n"
                f"2. A specific image prompt for visual assets.\n"
                f"Format the output clearly so the next agent can understand."
            ),
            agent=self.planner_agent,
            expected_output="A plan containing 'Text Prompt: ...' and 'Image Prompt: ...'"
        )

        # Task 2: Generate Content
        generation_task = Task(
            description=(
                "Based on the plan provided, use the Text Generation Tool to write the marketing copy "
                "and the Image Generation Tool to create the visual asset.\n"
                "Execute both tools."
            ),
            agent=self.content_agent,
            expected_output="Final generated text and the URL of the generated image.",
            context=[planning_task]
        )

        # Task 3: Validate Content
        validation_task = Task(
            description=(
                "Validate the generated text content using the Brand Validation Tool.\n"
                "Check for forbidden words and ensure tone consistency."
            ),
            agent=self.validator_agent,
            expected_output="Validation results indicating if the content is approved or rejected.",
            context=[generation_task]
        )

        crew = Crew(
            agents=[self.planner_agent, self.content_agent, self.validator_agent],
            tasks=[planning_task, generation_task, validation_task],
            verbose=True,
            memory=False
        )

        result = crew.kickoff()
        return result
