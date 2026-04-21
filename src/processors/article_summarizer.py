from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from pydantic import BaseModel

from src.processors.openai_client import OpenAIClient


class ArticleSummarizer:
  def __init__(self, config: dict):
    self._openai_client: OpenAIClient = OpenAIClient(config)
  
  def _summarize_one(self, web_result: dict[str, Any], prompt: str, response_format: BaseModel) -> dict[str, Any]:
    response = self._openai_client.invoke(
        inputs = str(web_result),
        prompt = prompt,
        response_format = response_format
    )
    return response
  
  def _summarize_all(self, web_results: list[dict[str, Any]], prompt: str, response_format: BaseModel) -> list[BaseModel]:
    results = []
    for web_result in web_results:
      try:
        results.append(self._summarize_one(web_result, prompt, response_format))
      except Exception as e:
        continue
    return results

  def _summarize_all_parallel(self, web_results: list[dict[str, Any]], prompt: str, response_format: BaseModel, max_workers: int = 5) -> list[BaseModel]:
    results = []
    with ThreadPoolExecutor(max_workers = max_workers) as executor:
      futures = [
          executor.submit(self._summarize_one, web_result, prompt, response_format)
          for web_result in web_results
      ]
      for future in as_completed(futures):
        try:
          results.append(future.result())
        except Exception as e:
          continue
    return results