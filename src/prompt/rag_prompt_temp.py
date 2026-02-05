"""
RAG Retrieval Prompts and Templates
"""

# Tool description for CrewAI
BRAND_RETRIEVER_DESCRIPTION = (
    "Retrieves specific brand guideline information including voice, tone, "
    "target audience, visual identity, and messaging framework. "
    "Input should be a focused question about brand guidelines."
)

# Output formatting templates
RETRIEVAL_OUTPUT_TEMPLATE = """Brand Guideline Information:

{results}
"""

RESULT_ENTRY_TEMPLATE = """[Result {rank} - Relevance: {relevance:.2%}]
{text}

{separator}
"""

NO_RESULTS_MESSAGE = "No relevant brand guideline information found."

RETRIEVAL_ERROR_TEMPLATE = "Error retrieving brand guidelines: {error}"


def format_retrieval_results(results: list) -> str:
    """
    Format retrieval results using template.
    
    Args:
        results: List of dicts with 'text', 'relevance', 'rank' keys
        
    Returns:
        Formatted output string
    """
    if not results:
        return NO_RESULTS_MESSAGE
    
    formatted_results = []
    for res in results:
        entry = RESULT_ENTRY_TEMPLATE.format(
            rank=res['rank'],
            relevance=res['relevance'],
            text=res['text'],
            separator="-" * 60
        )
        formatted_results.append(entry)
    
    return RETRIEVAL_OUTPUT_TEMPLATE.format(
        results="\n".join(formatted_results)
    ).strip()
