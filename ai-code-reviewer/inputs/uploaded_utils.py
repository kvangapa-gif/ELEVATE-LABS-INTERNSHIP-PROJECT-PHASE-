# core/utils.py


import json


from pathlib import Path


from typing import Any, Dict


def read_file(path: str) -> str:

    return Path(path).read_text(encoding="utf-8")


def write_file(path: str, content: str) -> None:

    Path(path).write_text(content, encoding="utf-8")


def save_json(path: str, data: Dict[str, Any]) -> None:

    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_json(path: str) -> Dict[str, Any]:

    return json.loads(Path(path).read_text(encoding="utf-8"))
