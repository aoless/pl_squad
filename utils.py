import json
import os
from typing import Any, Dict, List, Union

from loguru import logger

Json = Union[Dict[str, Any], List[Any]]


def load_json_cache(path: str) -> dict:
    if not os.path.exists(path):
        logger.warning("Cache file not found: {}", path)
        return {}
    with open(path, "r") as f:
        return json.load(f)
