from crewai import Crew, Task, Agent
from langchain_groq import ChatGroq
import logging
import os
from src.core.campaign_planner_agent import CampaignPlannerAgent
from src.core.brand_validation_agent import BrandValidationAgent
from src.core.content_generation_agent import ContentGenerationAgent
from src.prompt.planner_temp import get_planning_task_description, PLANNING_EXPECTED_OUTPUT

logger = logging.getLogger(__name__)

class ContentOrchestrationCrew:
    def __init__(self):
        logger.info("Initializing ContentOrchestrationCrew...")
        
        if os.getenv("GROQ_API_KEY"):
            os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
            os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
            logger.debug("Configured Groq API compatibility layer")

        # Initialize Groq LLMs
        self.planning_llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.writing_llm = ChatGroq(
            model_name="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY")
        )

        # Create agents from modular agent files
        self.planner_agent = CampaignPlannerAgent().create(llm=self.planning_llm)
        self.validator_agent = BrandValidationAgent().create(llm=self.planning_llm)
        self.content_agent = ContentGenerationAgent().create(llm=self.writing_llm)

    def run_campaign(self, inputs: dict) -> dict:
        campaign_name = inputs.get('campaign_name', 'Unknown')
        brand = inputs.get('brand', 'Unknown')
        objective = inputs.get('objective', 'Not specified')
        logger.info(f"Starting campaign orchestration: '{campaign_name}' for {brand}")
        
        try:
            # Use prompt template from planner_temp.py
            planning_task = Task(
                description=get_planning_task_description(
                    brand=brand,
                    campaign_name=campaign_name,
                    objective=objective
                ),
                agent=self.planner_agent,
                expected_output=PLANNING_EXPECTED_OUTPUT
            )

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
            
            logger.info(f"Launching crew for campaign '{campaign_name}'...")
            result = crew.kickoff()
            logger.info(f"Campaign '{campaign_name}' orchestration completed successfully")
            return result
        
        except Exception as e:
            logger.error(f"Campaign '{campaign_name}' orchestration failed: {e}", exc_info=True)
            raise

    def run_campaign_with_retry(self, inputs: dict, max_retries: int = 3) -> dict:
        from src.core.regeneration import run_campaign_with_regeneration
        return run_campaign_with_regeneration(self, inputs, max_retries)

