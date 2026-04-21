import arxiv
from typing import Any

class ArxivClient:
  def __init__(self):
    self._client = arxiv.Client()

  def fetch(self, web_results):
    list_ids = self._list_ids(web_results)
    if not list_ids:
      return []

    get_papers_by_ids = self._get_papers_by_ids(list_ids)

    return self._parse(get_papers_by_ids)

  def _list_ids(self, web_results: list[dict[str, Any]]) -> list[str]:
    ids = []
    for item in web_results:
      if item.get("source") == "arxiv":
        raw_id = item["link"].split("/")[-1]
        clean_id = raw_id.replace(".pdf", "").split("v")[0]
        ids.append(clean_id)
    return ids

  def _get_papers_by_ids(self, ids: list[str]) -> list[Any]:
    raw = list(self._client.results(arxiv.Search(id_list = ids)))
    return raw

  def _parse(self, raw: list[Any]) -> list[dict[str, Any]]:
    results = [
        {
            "title": getattr(paper, "title", ""),
            "link": getattr(paper, "links", [{}])[0].href,
            "snippet": getattr(paper, "summary", ""),
            "date": getattr(paper, "updated", "").strftime("%Y-%m-%d"), # type: ignore
            "source": "arxiv"
        } for paper in raw
    ]
    return results