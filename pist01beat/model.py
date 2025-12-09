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

        Expected keys in the returned dict:
        - engine_version
        - home_team
        - away_team
        - model_spread
        - model_total
        plus any debug payload from the engines.
        """
        result = self.integration_engine.run(home_team, away_team)
        return result
