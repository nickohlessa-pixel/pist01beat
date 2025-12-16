from __future__ import annotations

from typing import Any, Dict
import hashlib
import json

EXPORT_HASH_VERSION = "export_hash_v1_readonly"


def hash_export(export: Dict[str, Any]) -> str:
    """
    Deterministic SHA256 hash of a normalized export snapshot.

    Rules:
    - Stable key ordering (sorted)
    - JSON-serializable normalization
    - No I/O
    - No engine dependencies
    """
    normalized = _to_jsonable(export, path="")
    payload = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),  # stable, no whitespace variance
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _to_jsonable(x: Any, path: str) -> Any:
    # JSON scalars
    if x is None or isinstance(x, (bool, int, float, str)):
        return x

    # Dict: sort keys deterministically, coerce keys to str
    if isinstance(x, dict):
        out: Dict[str, Any] = {}
        for k in sorted(x.keys(), key=lambda z: str(z)):
            ks = str(k)
            child_path = f"{path}.{ks}" if path else ks
            out[ks] = _to_jsonable(x[k], child_path)
        return out

    # List: preserve order (treat as value container)
    if isinstance(x, list):
        return [_to_jsonable(v, f"{path}[{i}]") for i, v in enumerate(x)]

    # Unknown: coerce to repr so we remain JSON-serializable + deterministic
    return repr(x)
