import urllib.request

from bs4 import BeautifulSoup


def fetch_webpage(url: str) -> str:
    """Fetch and extract the text content of a webpage.

    Use this tool after web_search to read the full content of a specific URL.
    Also use this when a question provides a specific URL to look up.

    Args:
        url: The full URL of the webpage to fetch.

    Returns:
        The text content of the webpage, truncated if very long.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; research-agent/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")

        soup = BeautifulSoup(html, "html.parser")

        # remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # collapse multiple blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)

        # truncate text if too long
        max_chars = 15000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Content truncated...]"

        return text if text else "No text content found on the page."
    except Exception as e:
        return f"Error fetching webpage: {str(e)}"
