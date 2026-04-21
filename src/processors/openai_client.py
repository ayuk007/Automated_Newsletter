from openai import OpenAI
from pydantic import BaseModel
from typing import Any

from src.utils.helpers import require_env


class OpenAIClient:
  def __init__(self, config: dict):
    self._api_key = require_env("OPENAI_API_KEY")
    self._client = OpenAI(api_key = self._api_key)
    self._model = config["search"].get("model", "gpt-4o-mini")

  def invoke(self, inputs: Any, prompt: str, response_format) -> Any:
    messages = self._prepare_messsages(inputs, prompt)
    response = self._invoke(messages, response_format)

    return response

  def _prepare_messsages(self, inputs: Any, prompt: str) -> list[dict[str, str]]:
    messages = [
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": inputs
        }
    ]

    return messages

  def _invoke(self, messages: list[dict[str, str]], response_format: BaseModel) -> Any:
    response = self._client.beta.chat.completions.parse(
        model = self._model,
        messages = messages, # type: ignore
        response_format = response_format # type: ignore
    )

    return response.choices[0].message.parsed