# FILE: load_config.py
"""
Centralized loader and validator for Pist01 Beat v3.4 configuration.

This module is the single gateway for accessing:
- config.py (team profiles, baselines, thresholds)
- constants.py (global constants, model metadata)

It:
- imports config + constants
- validates required keys and structures
- exposes safe accessors for other engines

All engines should use this module instead of importing config.py directly.
"""

from typing import Any, Dict, Optional

import importlib

# Local imports (all should live in the same directory)
import config
import constants
from errors import ConfigError


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _require_key(mapping: Dict[str, Any], key: str, context: str) -> Any:
    """
    Ensure a given key exists in a mapping, otherwise raise ConfigError.
    """
    if key not in mapping:
        raise ConfigError(f"Missing key '{key}' in {context}.")
    return mapping[key]


def _validate_number(value: Any, context: str) -> None:
    """
    Ensure value is an int/float and not None.
    """
    if not isinstance(value, (int, float)):
        raise ConfigError(f"Expected numeric value for {context}, got {type(value).__name__}.")


# ============================================================
# PUBLIC METADATA ACCESS
# =========================
