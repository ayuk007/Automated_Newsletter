import httpx
from typing import Any
from src.utils.helpers import retry, require_env

SERPER_END_POINT = "https://google.serper.dev/search"

class SerperClient:
  def __init__(self, config: dict):
    self._api_key = require_env("SERPER_API_KEY")
    self._query: str = config["search"]["query"]
    self._domains: list[str] = config["search"].get("domains", [])
    self._num_results: int = config["search"].get("num_results", 20)
    self._keywords: list[str] = config["search"].get("keywords", [])
    self._num_pages: int = config["search"].get("num_pages", 2)
    self._time_range: str = config["search"].get("time_range", "qdr:w")
    self._auto_correct: bool = config["search"].get("auto_correct", False)
    self._search_language: str = config["search"].get("search_language", "en")

  def fetch(self) -> list[dict[str, Any]]:
    query = self._build_query()
    raw = self._search(query)
    results = self._parse(raw)

    return results

  def _build_query(self) -> str:
    if not self._domains:
      return self._query
    site_filter = "(" + " OR ".join(f"site:{d}" for d in self._domains) + ")"
    keywords_filter = "(" + " OR ".join(f'\\\"{k}\\\"' for k in self._keywords) + ")"
    final_query = f"{site_filter} AND {keywords_filter}"
    return final_query

  @retry(max_attempts = 3, delay = 2.0, exceptions = (httpx.HTTPError, Exception))
  def _search(self, query: str) -> dict[str, Any]:
    headers = {
        "X-API-KEY": self._api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "q": query,
        "num": self._num_results,
        "hl": self._search_language,
        "autocorrect": self._auto_correct,
        "tbs": self._time_range,
        "page": self._num_pages,
    }

    with httpx.Client(timeout = 30) as client:
      response = client.post(
          url = SERPER_END_POINT,
          headers = headers,
          json = payload
      )
      response.raise_for_status()
      return response.json()

  @staticmethod
  def _parse(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract organic results from Serper response."""
    organic = raw.get("organic", [])
    results = []
    for item in organic:
        results.append(
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": _classify_source(item.get("link", "")),
            }
        )
    return results

def _classify_source(url: str) -> str:
    """Classify a URL as 'arxiv', 'blog', or 'other'."""
    if "arxiv.org" in url:
        return "arxiv"
    blog_domains = {
      "openai.com",
      "deepmind.google",
      "huggingface.co",
      "ai.googleblog.com",
      "anthropic.com",
      "pytorch.org",
      "paperswithcode.com",
      "towardsdatascience.com",
      "sebastianraschka.com",
      "ai.meta.com",
      "mistral.ai",
      "huggingface.co",
      "allenai.org",
      "microsoft.com"
    }
    if any(d in url for d in blog_domains):
        return "blog"
    return "other"
