"""
Campaign Planning Task Prompts
"""

PLANNING_TASK_TEMPLATE = """
Analyze the campaign request for '{brand}' campaign '{campaign_name}'.

Objective: {objective}

Create a detailed plan that specifies:
1. A specific text prompt for marketing copy.
2. A specific image prompt for visual assets.

Format the output clearly so the next agent can understand.
"""

PLANNING_EXPECTED_OUTPUT = "A plan containing 'Text Prompt: ...' and 'Image Prompt: ...'"


def get_planning_task_description(brand: str, campaign_name: str, objective: str) -> str:
    """Generate planning task description from template"""
    return PLANNING_TASK_TEMPLATE.format(
        brand=brand,
        campaign_name=campaign_name,
        objective=objective
    )
