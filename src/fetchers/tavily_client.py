from tavily import TavilyClient
from typing import Any, Literal

from src.utils.helpers import require_env, list_non_arxiv_urls
from src.processors.article_summarizer import ArticleSummarizer
from src.schemas import TavilySummarizeItem



class TavilySearchClient:
  def __init__(self, config: dict):
    self._api_key = require_env("TAVILY_API_KEY")
    self._client = TavilyClient(api_key = self._api_key)
    self.extract_depth: Literal["basic", "advanced"] = config["search"].get("extract_depth", "basic")
    self.include_images: bool = config["search"].get("include_images", False)
    self.format: Literal["text", "markdown"] = config["search"].get("format", "markdown")
    self.article_summarizer = ArticleSummarizer(config)
  
  def fetch(self, web_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    urls = list_non_arxiv_urls(web_results)
    if not urls:
      return []
    raw_results = self._extract_batch(urls)
    return self.article_summarizer._summarize_all(raw_results, TAVILY_SUMMARIZE_PROMPT, TavilySummarizeItem) # type: ignore

  def _extract_by_url(self, url: str) -> dict[str, Any]:
    response = self._client.extract(
        url = url,
        extract_depth = self.extract_depth,
        include_images = self.include_images,
        format = self.format
    )
    return {
        "url": url,
        "content": response["results"][0]["raw_content"]
    }

  def _extract_batch(self, urls: list[str]) -> list[dict[str, Any]]:
    results = []
    for url in urls:
      results.append(self._extract_by_url(url))
    return results