"""Fetch webpage content tool."""

import requests
from bs4 import BeautifulSoup


def fetch_webpage(url: str) -> str:
    """Fetch and extract text content from a web page.

    Use this tool to retrieve the full text content of a web page when you
    have a specific URL and need to read its contents in detail.

    Args:
        url: The URL of the web page to fetch.

    Returns:
        The extracted text content of the web page.
    """
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
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text[:10000]
    except Exception as e:
        return f"Error fetching {url}: {e}"
