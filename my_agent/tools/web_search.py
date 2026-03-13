from ddgs import DDGS


def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return results.

    Use this tool when you need to find information on the internet, look up
    current facts, find URLs for specific topics, or answer questions that
    require up-to-date web knowledge.

    Args:
        query: The search query string.

    Returns:
        A list of search results with titles, URLs, and snippets.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=8))

        if not results:
            return "No search results found."

        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            url = r.get("href", r.get("link", "No URL"))
            snippet = r.get("body", r.get("snippet", "No snippet"))
            formatted.append(f"{i}. {title}\n   URL: {url}\n   {snippet}")

        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error performing web search: {str(e)}"
