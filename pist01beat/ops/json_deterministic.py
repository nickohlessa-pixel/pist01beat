"""
pist01beat.ops.json_deterministic

Deterministic JSON helpers for ops tooling.
Infrastructure-only. No engine imports.
"""

from __future__ import annotations

import json
from typing import Any


JSON_DETERMINISTIC_VERSION = "json_deterministic_v1_readonly"


def dumps(obj: Any) -> str:
    """
    Deterministic JSON string:
    - UTF-8 safe (ensure_ascii=False)
    - Stable key ordering (sort_keys=True)
    - Stable separators ("," ":")
    """
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def dump_to_path(obj: Any, path: str) -> None:
    """
    Writes deterministic JSON to `path` with a trailing newline.
    """
    payload = dumps(obj)
    with open(path, "w", encoding="utf-8") as f:
        f.write(payload + "\n")
