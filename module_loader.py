# FILE: module_loader.py
"""
Centralized, lazy engine loader for Pist01 Beat v3.4.

This module:
- Provides SAFE, LAZY, DYNAMIC loading of engine modules.
- Helps prevent circular imports by deferring imports until call time.
- Safely attempts to load engines when needed and reports clear errors.

All engine modules are assumed to live at the repo root (no packages).
Importing this file must never fail; only calling the loader functions
may raise EngineLoadError.
"""

from importlib import import_module
from typing import Any, Dict

# ============================================================
# ERROR TYPE SETUP
# ============================================================

try:
    # Prefer the project's EngineStateError if available.
    # We alias it to EngineLoadError so callers can always rely
    # on a single public exception type from this module.
    from errors import EngineStateError as EngineLoadError  # type: ignore[attr-defined]
except Exception:
    class EngineLoadError(Exception):
        """Fallback engine-load exception used when errors.EngineStateError is unavailable."""


# ============================================================
# ENGINE REGISTRY
# ============================================================

ENGINE_SPEC: Dict[str, Dict[str, str]] = {
    "identity": {
        "module": "identity_engine",
        "attr": "IdentityEngine",
    },
    "chaos": {
        "module": "chaos_engine",
        "attr": "ChaosEngine",
    },
    "volatility": {
        "module": "volatility_engine",
        "attr": "VolatilityEngine",
    },
    "integration": {
        "module": "integration_engine",
        "attr": "IntegrationEngine",
    },
}


# ============================================================
# CORE LOADERS
# ============================================================

def load_engine(name: str) -> Any:
    """
    Lazily load a single engine by its logical name.

    Parameters
    ----------
    name : str
        One of: "identity", "chaos", "volatility", "integration".

    Returns
    -------
    Any
        The loaded engine class or callable (e.g., IdentityEngine).

    Raises
    ------
    EngineLoadError
        If the name is unknown, the module cannot be imported,
        or the expected attribute is missing.
    """
    if name not in ENGINE_SPEC:
        known = ", ".join(sorted(ENGINE_SPEC.keys()))
        raise EngineLoadError(
            f"Unknown engine name {name!r}. "
            f"Known engines: {known}."
        )

    spec = ENGINE_SPEC[name]
    module_name = spec.get("module")
    attr_name = spec.get("attr")

    if not module_name or not attr_name:
        raise EngineLoadError(
            f"ENGINE_SPEC entry for {name!r} is malformed: {spec!r}"
        )

    try:
        module = import_module(module_name)
    except Exception as exc:  # ImportError or anything raised inside module import
        raise EngineLoadError(
            f"Failed to import engine module {module_name!r} "
            f"for engine {name!r}: {exc}"
        ) from exc

    try:
        engine_obj = getattr(module, attr_name)
    except AttributeError as exc:
        raise EngineLoadError(
            f"Engine attribute {attr_name!r} not found in module {module_name!r} "
            f"for engine {name!r}."
        ) from exc

    return engine_obj


def load_all_engines() -> Dict[str, Any]:
    """
    Attempt to load all engines defined in ENGINE_SPEC.

    Returns
    -------
    Dict[str, Any]
        Mapping of engine_name -> loaded engine object.

    Raises
    ------
    EngineLoadError
        If ANY engine fails to load. The error message will summarize
        all failures encountered.
    """
    loaded: Dict[str, Any] = {}
    failures: Dict[str, str] = {}

    for name in ENGINE_SPEC.keys():
        try:
            loaded[name] = load_engine(name)
        except EngineLoadError as exc:
            failures[name] = str(exc)

    if failures:
        summary_parts = [
            f"{engine_name!r}: {message}"
            for engine_name, message in failures.items()
        ]
        summary = "; ".join(summary_parts)
        raise EngineLoadError(
            f"Failed to load one or more engines: {summary}"
        )

    return loaded


def available_engines() -> Dict[str, bool]:
    """
    Probe which engines are currently loadable.

    This function MUST NEVER raise; all errors are swallowed internally.

    Returns
    -------
    Dict[str, bool]
        Mapping of engine_name -> True if loadable, False otherwise.
    """
    availability: Dict[str, bool] = {}

    for name in ENGINE_SPEC.keys():
        try:
            _ = load_engine(name)
            availability[name] = True
        except Exception:
            # Swallow all exceptions and just report False.
            availability[name] = False

    return availability


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    "ENGINE_SPEC",
    "EngineLoadError",
    "load_engine",
    "load_all_engines",
    "available_engines",
]
