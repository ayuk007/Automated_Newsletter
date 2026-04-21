import os
import time
from functools import wraps
from typing import Callable, Any, TypeVar

F = TypeVar("F", bound = Callable[..., Any])

def retry(
    max_attempts: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable[[F], F]:

  def decorator(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      current_delay = delay
      for attempt in range(1, max_attempts + 1):
        try:
          return func(*args, **kwargs)
        except exceptions as e:
          if attempt == max_attempts:
            raise
          time.sleep(current_delay)
          current_delay *= backoff
    return wrapper # type: ignore
  return decorator


def require_env(key: str) -> str:
    """
    Return the value of an environment variable.

    Raises:
        EnvironmentError: If the variable is not set.
    """
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set."
        )
    return value

import re
def resolve_env_vars(obj: Any) -> Any:
    """
    Recursively resolve '${VAR}' placeholders in a config dict/list/string.
    """
    if isinstance(obj, dict):
        return {k: resolve_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_env_vars(v) for v in obj]
    if isinstance(obj, str):
        return re.sub(
            r"\$\{([^}]+)\}",
            lambda m: os.environ.get(m.group(1), m.group(0)),
            obj,
        )
    return obj

def list_non_arxiv_urls(web_results: list[dict[str, Any]]) -> list[str]:
    urls = []
    for item in web_results:
      if item.get("source") != "arxiv":
        urls.append(item["link"])
    return urls