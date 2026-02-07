from crewai import Crew, Task, Agent
import logging
import os
import re
from typing import Dict, Any
from src.core.campaign_planner_agent import CampaignPlannerAgent
from src.core.brand_validation_agent import BrandValidationAgent
from src.core.content_generation_agent import ContentGenerationAgent
from src.prompt.planner_temp import get_planning_task_description, PLANNING_EXPECTED_OUTPUT

logger = logging.getLogger(__name__)

class ContentOrchestrationCrew:
    def __init__(self):
        logger.info("Initializing ContentOrchestrationCrew...")
        
        # Load model configuration from config file
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '../../config/model.config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Configure Groq API key
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        os.environ["GROQ_API_KEY"] = groq_api_key
        logger.debug(f"Configured Groq API (key: {groq_api_key[:15]}...)")

        # Load models from config
        campaign_planner_config = config['agents']['campaign_planner']
        brand_validator_config = config['agents']['brand_validator']
        
        self.planning_llm = campaign_planner_config['models']['planning']  # groq/llama-3.3-70b-versatile
        self.writing_llm = campaign_planner_config['models']['writing']    # groq/llama-3.1-8b-instant
        self.validator_llm = brand_validator_config['model']               # groq/llama-3.3-70b-versatile

        # Create agents from modular agent files
        self.planner_agent = CampaignPlannerAgent().create(llm=self.planning_llm)
        self.validator_agent = BrandValidationAgent().create(llm=self.validator_llm)
        self.content_agent = ContentGenerationAgent().create(llm=self.writing_llm)

    def run_campaign(self, inputs: dict) -> dict:
        import time
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

        campaign_name = inputs.get('campaign_name', 'Unknown')
        brand = inputs.get('brand', 'Unknown')
        logger.info(f"Starting campaign orchestration: '{campaign_name}' for {brand}")
        
        # Custom Retry Decorator for Groq API Rate Limits
        def log_retry(retry_state):
            logger.warning(f"⚠️ Rate limit hit. Retrying attempt {retry_state.attempt_number}...")

        @retry(
            wait=wait_exponential(multiplier=2, min=5, max=60),
            stop=stop_after_attempt(5),
            retry=retry_if_exception_type(Exception), # Ideally catch specific RateLimitError if imported
            before_sleep=log_retry
        )
        def robust_kickoff(crew, inputs=None):
            return crew.kickoff(inputs=inputs)

        try:
            # --- STAGE 1: PLAN CAMPAIGN ---
            logger.info("🎬 STAGE 1: Planning Strategy...")
            planning_task = Task(
                description=f"Create campaign plan for {campaign_name}. Use RAG tool for brand guidelines. Keep concise.",
                agent=self.planner_agent,
                expected_output="Campaign plan."
            )
            
            planning_crew = Crew(
                agents=[self.planner_agent],
                tasks=[planning_task],
                verbose=True
            )
            plan_result = robust_kickoff(planning_crew, inputs=inputs)
            logger.info("✅ Stage 1 Complete.")

            # --- STAGE 2: VALIDATE PLAN ---
            logger.info("🛡️ STAGE 2: Validating Plan...")
            plan_str = str(plan_result)
            
            plan_validation_task = Task(
                description=f"Review this plan: '''{plan_str}'''\n\nCheck brand compliance. Reply 'APPROVED' or give feedback.",
                agent=self.validator_agent,
                expected_output="APPROVED or feedback."
            )
            
            validation_crew = Crew(
                agents=[self.validator_agent],
                tasks=[plan_validation_task],
                verbose=True
            )
            validation_result = robust_kickoff(validation_crew)
            logger.info("✅ Stage 2 Complete.")
            
            # Check validation content
            validation_str = str(validation_result)

            # --- STAGE 3a: TEXT GENERATION ---
            logger.info("✍️ STAGE 3a: Generating Text Content...")
            
            text_generation_task = Task(
                description=(
                    "Use the 'Text Generation Tool' to write marketing copy for the FitNow campaign. "
                    "Pass this exact prompt to the tool:\n"
                    "'Write compelling marketing copy for the FitNow New Year Wellness Journey campaign. "
                    "Include a catchy headline, 2-3 short paragraphs about building healthy habits and community support, "
                    "and a call-to-action. Keep it motivational and concise.'\n"
                    "Do not add any other text. Just return the tool's output."
                ),
                agent=self.content_agent,
                expected_output="Actual marketing copy generated by calling the Text Generation Tool."
            )
            
            text_crew = Crew(
                agents=[self.content_agent],
                tasks=[text_generation_task],
                verbose=True
            )
            text_result = robust_kickoff(text_crew)
            logger.info("✅ Stage 3a Complete (Text Generated).")
            
            # --- STAGE 3b: IMAGE GENERATION ---
            logger.info("🎨 STAGE 3b: Generating Image...")
            
            image_generation_task = Task(
                description=(
                    "You MUST execute the 'Image Generation Tool' to create the image. "
                    "1. Call the tool with this prompt: "
                    "'A serene wellness scene with a person in athletic wear meditating outdoors at sunrise, "
                    "surrounded by nature. Calming blue and white tones. Modern, inspiring aesthetic.'\n"
                    "2. The tool will generate a real file and return a success message with a URL. "
                    "3. Return ONLY that URL. Do not invent a path.\n"
                    "CRITICAL: Use ONLY the 'Image Generation Tool'. Do NOT try to use 'brave_search', 'google_search', or any other tool. "
                    "If the tool is not available, fail the task."
                ),
                agent=self.content_agent,
                expected_output="Image path/URL returned by the Image Generation Tool."
            )
            
            image_crew = Crew(
                agents=[self.content_agent],
                tasks=[image_generation_task],
                verbose=True
            )
            image_result = robust_kickoff(image_crew)
            
            logger.info(f"Campaign '{campaign_name}' orchestration completed successfully")
            
            # Combine results (return both text and image)
            final_result = {
                "text": str(text_result),
                "image": str(image_result),
                "plan": plan_str,
                "validation": validation_str
            }
            return final_result
        
        except Exception as e:
            logger.error(f"Campaign '{campaign_name}' orchestration failed: {e}", exc_info=True)
            raise

    def run_with_auto_regeneration(self, inputs: Dict[str, Any], max_attempts: int = 3) -> Dict[str, Any]:
        """
        Run campaign with automatic PLAN regeneration on validation failure.
        
        CORRECT WORKFLOW:
        1. RAG extracts brand context
        2. Planner creates campaign plan
        3. Brand Validator validates THE PLAN
        4. If plan APPROVED → Generate content (text + image)
        5. If plan REJECTED → Regenerate plan with validator feedback (loop to step 2)
        
        Args:
            inputs: Campaign inputs (campaign_name, brand, objective, etc.)
            max_attempts: Maximum number of plan generation attempts
            
        Returns:
            dict with:
                - status: 'approved' or 'failed_after_retries'
                - attempts: number of plan generation tries
                - result: CrewAI output (includes plan and content if approved)
                - validation_summary: validation result info
        """
        campaign_name = inputs.get('campaign_name', 'Unknown')
        logger.info(f"Starting auto-regeneration workflow for '{campaign_name}' (max attempts: {max_attempts})")
        logger.info("Workflow: RAG → Plan → Validate PLAN → (approved) Generate Content | (rejected) Regenerate Plan")
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"🔄 Plan Generation Attempt {attempt}/{max_attempts} for campaign '{campaign_name}'")
            
            # Run the campaign (RAG → Plan → Validate Plan → Content if approved)
            result = self.run_campaign(inputs)
            
            # Extract and parse plan validation result
            validation_info = self._extract_plan_validation_info(result)
            
            logger.info(f"Plan Validation Status: {validation_info['status']}")
            
            if validation_info['status'] == 'approved':
                logger.info(f"✅ Campaign plan approved on attempt {attempt}. Content generated successfully.")
                return {
                    'status': 'approved',
                    'attempts': attempt,
                    'result': result,
                    'validation_summary': validation_info
                }
            
            # If not last attempt, enhance objective for plan regeneration
            if attempt < max_attempts:
                logger.warning(f"⚠️ Plan validation failed on attempt {attempt}. Regenerating plan with feedback...")
                inputs = self._enhance_objective_for_plan_retry(
                    inputs, validation_info, attempt
                )
            else:
                logger.error(f"❌ Plan validation failed after {max_attempts} attempts")
        
        return {
            'status': 'failed_after_retries',
            'attempts': max_attempts,
            'result': result,
            'validation_summary': validation_info
        }
    
    def _extract_plan_validation_info(self, crew_output) -> Dict[str, Any]:
        """
        Extract PLAN validation information from CrewAI output.
        Parse for plan approval/rejection signals and feedback.
        
        Note: This validates the PLAN, not the final content.
        """
        result_str = str(crew_output).lower()
        
        # Check for plan approval/rejection signals
        rejection_keywords = ['rejected', 'invalid', 'not compliant', 'needs revision', 'revise']
        approval_keywords = ['approved', 'compliant', 'acceptable', 'good plan']
        
        has_rejection = any(keyword in result_str for keyword in rejection_keywords)
        has_approval = any(keyword in result_str for keyword in approval_keywords)
        
        # Extract specific feedback/violations
        feedback_items = []
        
        # Look for feedback patterns
        if 'feedback:' in result_str or 'suggestions:' in result_str:
            # Try to extract feedback section
            feedback_match = re.search(r'(?:feedback|suggestions):(.*?)(?=\n\n|\Z)', result_str, re.DOTALL)
            if feedback_match:
                feedback_items.append(f"Validator feedback: {feedback_match.group(1).strip()[:200]}")
        
        if 'tone' in result_str and ('incorrect' in result_str or 'inappropriate' in result_str):
            feedback_items.append("Tone does not match brand guidelines")
        
        if 'messaging' in result_str and ('unclear' in result_str or 'off-brand' in result_str):
            feedback_items.append("Messaging strategy needs revision")
        
        if 'target audience' in result_str and 'mismatch' in result_str:
            feedback_items.append("Target audience approach needs adjustment")
        
        # Determine status
        if has_rejection and not has_approval:
            status = 'rejected'
        elif has_approval and not has_rejection:
            status = 'approved'
        elif feedback_items:
            status = 'rejected'
        else:
            # Default to approved if no clear signals (assume plan is okay)
            status = 'approved'
        
        return {
            'status': status,
            'feedback': feedback_items if feedback_items else ['Plan needs improvement'],
            'raw_output': result_str[:300]  # Keep first 300 chars for debugging
        }
    
    def _enhance_objective_for_plan_retry(
        self, inputs: Dict[str, Any], validation_info: Dict[str, Any], attempt: int
    ) -> Dict[str, Any]:
        """
        Enhance campaign objective based on PLAN validation feedback.
        Adds specific guidance to help planner create compliant plan.
        
        This modifies the inputs for PLAN regeneration, not content regeneration.
        """
        enhanced = inputs.copy()
        
        feedback_items = validation_info.get('feedback', [])
        
        # Build enhancement message based on feedback
        guidance = []
        
        for feedback in feedback_items:
            if 'tone' in feedback.lower():
                guidance.append("Ensure campaign tone aligns strictly with brand voice guidelines")
            if 'messaging' in feedback.lower() or 'strategy' in feedback.lower():
                guidance.append("Revise messaging strategy to better align with brand positioning")
            if 'audience' in feedback.lower():
                guidance.append("Adjust target audience approach per brand guidelines")
            if 'feedback:' in feedback.lower():
                # Extract actual feedback text
                guidance.append(f"Address validator feedback: {feedback}")
        
        # Add progressive strictness
        if attempt >= 2:
            guidance.append("CRITICAL: Strict adherence to brand guidelines required")
        
        if guidance:
            enhancement = f"\n\n🔄 [Plan Revision Attempt {attempt + 1}] Brand Compliance Requirements:\n" + \
                         "\n".join(f"  • {g}" for g in guidance) + \
                         "\n\nPrevious plan feedback: " + "; ".join(feedback_items)
            
            if 'objective' in enhanced and enhanced['objective']:
                enhanced['objective'] = f"{enhanced['objective']}{enhancement}"
            else:
                enhanced['objective'] = enhancement
        
        logger.debug(f"Enhanced objective for plan retry attempt {attempt + 1}: {guidance}")
        return enhanced

    def run_campaign_with_retry(self, inputs: dict, max_retries: int = 3) -> dict:
        """Legacy method - redirects to new auto-regeneration"""
        return self.run_with_auto_regeneration(inputs, max_retries)

