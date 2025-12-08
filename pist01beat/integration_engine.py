# FILE: pist01beat/integration_engine.py
"""
Integration Engine v3.4 — Pist01 Beat

This module glues together the verified core engines:

- IdentityEngine   → baseline matchup identity (spread/total, style, etc.)
- ChaosEngine      → chaos_score + chaos_flag + debug
- VolatilityEngine → volatility_score + volatility_flag + debug

It exposes a small, deterministic IntegrationEngine that:
- Takes (home_team, away_team, optional notes)
- Calls each engine with those inputs
- Returns a single, unified state dict

This is a wiring layer only.
No NBA data, no betting logic, no external side effects.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .identity_engine import IdentityEngine
from .chaos_engine import ChaosEngine
from .volatility_engine import VolatilityEngine


# ============================================================
# Helpers
# ============================================================

def _normalize_result(result: Any) -> Dict[str, Any]:
    """
    Normalize engine outputs into a dict.

    Supports:
    - dict (returned as-is)
    - dataclass / simple object (uses .to_dict() if present, else __dict__)
    - None → {}
    """
    if result is None:
        return {}

    if isinstance(result, dict):
        return result

    # If the result has an explicit to_dict() method, prefer that.
    to_dict = getattr(result, "to_dict", None)
    if callable(to_dict):
        try:
            out = to_dict()  # type: ignore[no-any-return]
            if isinstance(out, dict):
                return out
        except Exception:
            pass

    # Fallback: use the object __dict__ if available.
    if hasattr(result, "__dict__"):
        return dict(result.__dict__)

    # Last resort: empty dict
    return {}


# ============================================================
# Core Integration Engine
# ============================================================

class IntegrationEngine:
    """
    Integration Engine v3.4

    Responsibilities:
    - Own instances of IdentityEngine, ChaosEngine, VolatilityEngine
    - Run them in a consistent order for a given matchup
    - Merge their outputs into a single structured state

    This engine does NOT:
    - Fetch or mutate any config
    - Make betting decisions
    - Know anything about real-world NBA data
    """

    ENGINE_VERSION = "3.4-integration"

    def __init__(
        self,
        identity_engine: Optional[IdentityEngine] = None,
        chaos_engine: Optional[ChaosEngine] = None,
        volatility_engine: Optional[VolatilityEngine] = None,
    ) -> None:
        # Allow dependency injection for tests, but default to real engines.
        self.identity_engine = identity_engine or IdentityEngine()
        self.chaos_engine = chaos_engine or ChaosEngine()
        self.volatility_engine = volatility_engine or VolatilityEngine()

    def compute_integrated_state(
        self,
        home_team: str,
        away_team: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compute the unified model state for a single matchup.

        Parameters
        ----------
        home_team : str
            Home team code (e.g., "HOR").
        away_team : str
            Away team code (e.g., "DEN").
        notes : Optional[str]
            Optional freeform notes/context for ChaosEngine.

        Returns
        -------
        Dict[str, Any]
            A structured dict combining identity, chaos, and volatility.
        """
        home_team = home_team.strip().upper()
        away_team = away_team.strip().upper()

        if not home_team or not away_team:
            raise ValueError("home_team and away_team must be non-empty strings.")

        if home_team == away_team:
            raise ValueError("home_team and away_team must be different teams.")

        # 1) Call core engines (raw objects)
        identity_raw = self.identity_engine.compute_identity(
            home_team=home_team,
            away_team=away_team,
        )

        chaos_raw = self.chaos_engine.compute_chaos(
            home_team=home_team,
            away_team=away_team,
            notes=notes,
        )

        volatility_raw = self.volatility_engine.compute_volatility(
            home_team=home_team,
            away_team=away_team,
        )

        # 2) Normalize to dicts so we can safely .get()
        identity = _normalize_result(identity_raw)
        chaos = _normalize_result(chaos_raw)
        volatility = _normalize_result(volatility_raw)

        # 3) Light summary lens across engines
        summary: Dict[str, Any] = {
            # Identity-derived
            "base_spread": identity.get("base_spread"),
            "base_total": identity.get("base_total"),
            "pace_factor": identity.get("pace_factor"),
            "power_diff": identity.get("power_diff"),
            # Chaos + volatility health flags
            "chaos_flag": chaos.get("chaos_flag"),
            "chaos_score": chaos.get("chaos_score"),
            "volatility_flag": volatility.get("volatility_flag"),
            "volatility_score": volatility.get("volatility_score"),
        }

        # 4) Full integrated state
        integrated_state: Dict[str, Any] = {
            "engine_version": self.ENGINE_VERSION,
            "home_team": home_team,
            "away_team": away_team,
            "summary": summary,
            "identity": identity,
            "chaos": chaos,
            "volatility": volatility,
            "debug": {
                "input": {
                    "home_team": home_team,
                    "away_team": away_team,
                    "notes": notes,
                },
                "identity_raw_type": type(identity_raw).__name__,
                "chaos_raw_type": type(chaos_raw).__name__,
                "volatility_raw_type": type(volatility_raw).__name__,
                "identity_debug": identity.get("debug"),
                "chaos_debug": chaos.get("debug"),
                "volatility_debug": volatility.get("debug"),
            },
        }

        return integrated_state


# ============================================================
# Convenience function
# ============================================================

def compute_integrated_state(
    home_team: str,
    away_team: str,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience wrapper so callers can do:

        from pist01beat.integration_engine import compute_integrated_state
        state = compute_integrated_state("HOR", "DEN")

    without manually instantiating IntegrationEngine.
    """
    engine = IntegrationEngine()
    return engine.compute_integrated_state(
        home_team=home_team,
        away_team=away_team,
        notes=notes,
    )


if __name__ == "__main__":
    # Simple smoke test / example usage (safe to ignore in production).
    from pprint import pprint

    demo = compute_integrated_state("HOR", "DEN")
    pprint(demo["summary"])
