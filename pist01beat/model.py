# FILE: pist01beat/model.py
"""
Pist01 Beat v3.4 — High-level wrapper.

Single public entrypoint:

    from pist01beat import Pist01Beat

This wrapper delegates the full pipeline to IntegrationEngine,
which calls the underlying engines and returns the final result.
"""

from typing import Any, Dict

from .integration_engine import IntegrationEngine


class Pist01Beat:
    """High-level Pist01 Beat v3.4 wrapper."""

    def __init__(self) -> None:
        # Orchestration layer that runs the full pipeline.
        self.integration_engine = IntegrationEngine()

    def predict(self, home_team: str, away_team: str) -> Dict[str, Any]:
        """
        Run the full v3.4 pipeline for a matchup.

        Returns:
        - engine_version
        - home_team
        - away_team
        - model_spread
        - model_total
        plus full engine state under 'debug'.
        """
        # Run the integration layer to get full engine state
        state = self.integration_engine.run(home_team=home_team, away_team=away_team)

        # Spread block comes from SpreadEngine via IntegrationEngine
        spread_block = state.get("spread", None)

        model_spread = None
        model_total = None

        if spread_block is not None:
            # Prefer dataclass attributes
            model_spread = getattr(spread_block, "model_spread", None)
            model_total = getattr(spread_block, "model_total", None)

            # Fallback if spread_block is dict-like
            if model_spread is None and isinstance(spread_block, dict):
                model_spread = spread_block.get("model_spread")
            if model_total is None and isinstance(spread_block, dict):
                model_total = spread_block.get("model_total")

        # Final safety defaults if something is missing
        if model_spread is None:
            model_spread = 0.0
        if model_total is None:
            model_total = 0.0

        return {
            "engine_version": state.get("engine_version", "3.4-model-v1"),
            "home_team": state.get("home_team", home_team),
            "away_team": state.get("away_team", away_team),
            "model_spread": model_spread,
            "model_total": model_total,
            "debug": state,
        }
