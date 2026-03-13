"""Web search tool using Serper or Tavily API.

Supports both Serper (serper.dev) and Tavily (tavily.com) providers.
Provider is selected automatically based on available API keys:
- If SERPER_API_KEY is set, uses Serper (default)
- If TAVILY_API_KEY is set, uses Tavily
"""

import json
import logging
import os

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


TOP_K = 5
MAX_DOC_LEN = 5000


def _fetch_url_content(url: str) -> str:
    """Fetch and extract text content from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        lines = (line.strip() for line in soup.get_text(separator="\n", strip=True).splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = "\n".join(chunk for chunk in chunks if chunk)
        logger.debug("Fetched %s (%d chars)", url, len(content))
        return content
    except Exception as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return ""


def _search_serper(query: str, api_key: str) -> list[dict]:
    """Search using Serper API and fetch full page content for each result."""
    logger.info("Serper search: %r", query)
    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": query, "num": TOP_K, "autocorrect": True},
        timeout=30,
    )
    response.raise_for_status()
    results = []
    for organic in response.json().get("organic", [])[:TOP_K]:
        url = organic.get("link", "")
        snippet = organic.get("snippet", "")
        content = _fetch_url_content(url) if url else ""
        results.append({
            "title": organic.get("title", ""),
            "url": url,
            "content": (content or snippet)[:MAX_DOC_LEN * 2],
        })
    logger.info("Serper returned %d results", len(results))
    return results


def _search_tavily(query: str, api_key: str) -> list[dict]:
    """Search using Tavily API (content provided directly by the API)."""
    from tavily import TavilyClient
    logger.info("Tavily search: %r", query)
    response = TavilyClient(api_key=api_key).search(
        query=query, search_depth="advanced", max_results=TOP_K
    )
    results = []
    for result in response.get("results", [])[:TOP_K]:
        content = result.get("content", "") or ""
        results.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": content[:MAX_DOC_LEN * 2],
        })
    logger.info("Tavily returned %d results", len(results))
    return results


def _format_results(results: list[dict], query: str) -> str:
    """Format search results into a document string."""
    if not results:
        return f"No results found for query: {query}"
    formatted = ""
    for i, doc in enumerate(results):
        formatted += f"**Web Page {i + 1}:**\n"
        formatted += json.dumps(
            {"title": doc.get("title", ""), "content": doc.get("content", "")},
            ensure_ascii=False,
            indent=2,
        ) + "\n"
    return formatted.strip()


def web_search(query: str) -> str:
    """Search the web and return results.

    Use this tool when you need to find information on the internet, look up
    current facts, find URLs for specific topics, or answer questions that
    require up-to-date web knowledge.

    Args:
        query: The search query string.

    Returns:
        A list of search results with titles, URLs, and snippets.
    """
    # NOTE: use tavily
    serper_key = None # os.getenv("SERPER_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    try:
        if serper_key:
            results = _search_serper(query, serper_key)
        elif tavily_key:
            results = _search_tavily(query, tavily_key)
        else:
            logger.error("No web search API key found (SERPER_API_KEY or TAVILY_API_KEY)")
            return "Error: No web search API key found. Set SERPER_API_KEY or TAVILY_API_KEY."
        formatted = _format_results(results, query)
        logger.debug("web_search result for %r:\n%s", query, formatted)
        print(f"web_search result for {query}:\n{formatted}")
        with open("results_search.txt", "a", encoding="utf-8") as f:
            f.write(f"Query: {query}\n{formatted}\n{'=' * 80}\n")
        return formatted
    except Exception as e:
        logger.error("web_search failed for %r: %s", query, e, exc_info=True)
        return f"Error performing web search: {e}"
