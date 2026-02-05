SYSTEM_PROMPT = """You are a helpful AI assistant specialized in creating high-quality marketing and general content. 
You provide clear, engaging, and professional responses."""

MARKETING_COPY_TEMPLATE = """Write compelling marketing copy for {brand}'s '{campaign_name}' campaign.

Objective: {objective}
{target_audience_section}
Generate engaging marketing copy that captures attention and drives action:"""

def build_marketing_copy_prompt(campaign_name: str, brand: str, objective: str, target_audience: str = None) -> str:
    target_section = f"Target Audience: {target_audience}\n" if target_audience else ""
    return MARKETING_COPY_TEMPLATE.format(
        brand=brand,
        campaign_name=campaign_name,
        objective=objective,
        target_audience_section=target_section
    )


TEXT_GENERATION_PROMPT = """Continue the following text in a natural and coherent way:

{prompt}"""

PRODUCT_DESCRIPTION_TEMPLATE = """Create a compelling product description for {product_name}.

Key Features:
{features}

Target Audience: {audience}

Generate a professional and engaging product description:"""
