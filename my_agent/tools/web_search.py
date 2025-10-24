import logging

logger = logging.getLogger(__name__)

def web_search(query: str) -> dict:
    """Performs a web search and returns the top results.

    Args:
        query (str): The search query.
        context (ToolContext): The tool execution context.

    Returns:
        dict: A dictionary containing the search results.
    Example:
        >>> web_search("What is the weather in Nairobi?", context)
        {'results': [{'title': ..., 'snippet': ..., 'url': ...}, ...]}
    """
    logger.info(f"Performing web search for query: {query}")
    # MOCK WEB SEARCH RESPONSE - Replace with actual web search API call
    result = {
        "results": [
            {
                "title": "Sample Web Result 1",
                "snippet": "This is a summary of the first search result for your query.",
                "url": "http://www.example.com/result1"
            },
            {
                "title": "Sample Web Result 2",
                "snippet": "This is a summary of the second search result.",
                "url": "http://www.example.com/result2"
            }
        ]
    }
    return result
