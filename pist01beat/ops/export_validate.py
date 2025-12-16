from __future__ import annotations

from typing import Any, Dict, List
import json

EXPORT_VALIDATE_VERSION = "export_validate_v1_readonly"

# Minimal shape contract for HB13 export snapshots
_REQUIRED_TOP_KEYS: List[str] = [
    "version",
    "context_snapshot",
    "decision_hash",
    "decision_log",
    "decision_timeline",
    "team_pack_audit",
    "warnings",
]


def validate_export(export: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a model export snapshot for basic sanity.

    Returns:
      {
        "ok": bool,
        "errors": [str, ...],
        "warnings": [str, ...]
      }
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(export, dict):
        return _finalize(False, ["export is not a dict"], ["coerced=False"])

    # Required key presence
    for k in _REQUIRED_TOP_KEYS:
        if k not in export:
            errors.append(f"missing top-level key: '{k}'")

    # Version type check
    if "version" in export and not isinstance(export.get("version"), str):
        warnings.append("top-level 'version' is not a string")

    # Warnings type check
    if "warnings" in export:
        wv = export.get("warnings")
        if wv is not None and not isinstance(wv, list):
            warnings.append("top-level 'warnings' is not a list (or None)")

    # JSON serializability check
    json_ok, json_note = _is_json_serializable(export)
    if not json_ok:
        warnings.append(f"export not strictly JSON-serializable: {json_note}")

    # Non-string dict keys (deep)
    non_string_paths = _find_non_string_dict_keys(export)
    if non_string_paths:
        sample = non_string_paths[:10]
        warnings.append(
            "non-string dict keys found at: " +
            ", ".join(sample) +
            (" (truncated)" if len(non_string_paths) > 10 else "")
        )

    ok = len(errors) == 0
    return _finalize(ok, errors, warnings)


def _finalize(ok: bool, errors: List[str], warnings: List[str]) -> Dict[str, Any]:
    return {
        "ok": bool(ok),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def _is_json_serializable(x: Any) -> (bool, str):
    try:
        json.dumps(x, sort_keys=True)
        return True, "ok"
    except TypeError as e:
        return False, str(e)


def _find_non_string_dict_keys(x: Any) -> List[str]:
    paths: List[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if not isinstance(k, str):
                    paths.append(path if path else "<root>")
                child = f"{path}.{k}" if path else str(k)
                walk(v, child)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                child = f"{path}[{i}]" if path else f"[{i}]"
                walk(v, child)

    walk(x, "")
    paths.sort()
    return paths
