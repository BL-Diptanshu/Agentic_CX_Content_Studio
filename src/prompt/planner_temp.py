"""
Campaign Planning Task Prompts with RAG Integration
Optimized for balanced token usage and clarity
"""

PLANNING_TASK_TEMPLATE = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMPAIGN PLANNING WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: RETRIEVE BRAND GUIDELINES (Mandatory)
Use the Brand Guideline Retriever tool to fetch:
- Brand voice and tone characteristics
- Target audience information  
- Forbidden language and terms to avoid
- Messaging framework and key themes

Query: "What are the brand voice, tone, and guidelines?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2: ANALYZE CAMPAIGN REQUEST

Brand: {brand}
Campaign: {campaign_name}
Objective: {objective}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3: CREATE BRAND-ALIGNED PLAN

Using retrieved brand guidelines, provide:

TEXT PROMPT:
- Reflect brand voice and tone
- Use brand-appropriate language
- Avoid forbidden terms
- Align with messaging framework

IMAGE PROMPT:
- Match brand visual identity
- Support messaging theme
- Align with brand aesthetics

{context_section}

FORMAT: Clearly separate "Text Prompt: ..." and "Image Prompt: ..."

CRITICAL: Your plan must explicitly reference the retrieved brand guidelines.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

PLANNING_EXPECTED_OUTPUT = "A plan with 'Text Prompt: ...' and 'Image Prompt: ...' that references brand guidelines"

BRAND_CONTEXT_TEMPLATE = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RETRIEVED BRAND GUIDELINES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def format_brand_context(context: str) -> str:
    """
    Format retrieved brand context with visual separators.
    
    Args:
        context: Raw brand context from RAG retrieval
        
    Returns:
        Formatted context string with visual separators, empty if no context
    """
    if not context or context.strip() == "":
        return ""
    
    return BRAND_CONTEXT_TEMPLATE.format(context=context.strip())


def get_planning_task_description(brand: str, campaign_name: str, objective: str) -> str:
    """
    Generate planning task description from template (without pre-fetched context).
    Agent will fetch context using RAG tool.
    
    Args:
        brand: Brand name
        campaign_name: Campaign name
        objective: Campaign objective
        
    Returns:
        Planning task description with RAG instructions
    """
    return PLANNING_TASK_TEMPLATE.format(
        brand=brand,
        campaign_name=campaign_name,
        objective=objective,
        context_section=""  # Agent fetches context via tool
    )


def get_planning_task_with_context(
    brand: str, 
    campaign_name: str, 
    objective: str,
    brand_context: str = ""
) -> str:
    """
    Generate planning task description with pre-fetched brand context (optional).
    
    Use this if you want to pre-fetch and inject brand context.
    Otherwise, use get_planning_task_description() and let agent fetch via tool.
    
    Args:
        brand: Brand name
        campaign_name: Campaign name
        objective: Campaign objective
        brand_context: Pre-fetched brand context (optional)
        
    Returns:
        Planning task description with context injection
    """
    context_section = format_brand_context(brand_context) if brand_context else ""
    
    return PLANNING_TASK_TEMPLATE.format(
        brand=brand,
        campaign_name=campaign_name,
        objective=objective,
        context_section=context_section
    )


