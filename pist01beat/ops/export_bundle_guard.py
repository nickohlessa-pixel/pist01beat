"""
pist01beat.ops.export_bundle_guard

Non-fatal schema/shape guard for audited export bundles.
Infrastructure-only. No engine imports.
"""

from __future__ import annotations

from typing import List


EXPORT_BUNDLE_GUARD_VERSION = "export_bundle_guard_v1_readonly"


_EXPECTED_KEYS = [
    "export",
    "validation",
    "export_hash",
    "stamp",
    "cli_warnings",
    "version",
]


def check_bundle_shape(bundle: dict) -> List[str]:
    """
    Returns non-fatal warnings:
      - "missing_key:<k>"
      - "extra_key:<k>"
    """
    warnings: List[str] = []
    if not isinstance(bundle, dict):
        return ["bundle_not_dict"]

    keys = set(bundle.keys())
    expected = set(_EXPECTED_KEYS)

    for k in _EXPECTED_KEYS:
        if k not in keys:
            warnings.append(f"missing_key:{k}")

    for k in sorted(list(keys - expected)):
        warnings.append(f"extra_key:{k}")

    return warnings
