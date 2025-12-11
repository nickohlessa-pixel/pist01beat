# FILE: pist01beat/calibration_engine.py
"""
Pist01 Beat v3.4 — Calibration Engine (v1)

Purpose:
- Measure how far off the model is on spread and total for each game.
- Provide simple aggregate stats overall and by team.
- Keep this purely numeric: no I/O, no dependencies on other pist01beat modules.

Usage pattern (in a notebook or calling code):

    from pist01beat.calibration_engine import (
        GameCalibrationInput,
        compute_game_calibration,
        CalibrationAccumulator,
    )

    # 1) For each finished game, build an input record
    inp = GameCalibrationInput(
        home_team="HOR",
        away_team="DEN",
        predicted_spread=model_spread,
        predicted_total=model_total,
        actual_home_score=105,
        actual_away_score=110,
        context="calibration",    # or "real_bet"
        notes="No major injuries"
    )

    # 2) Compute per-game calibration
    result = compute_game_calibration(inp)

    # 3) Add to an accumulator to track over many games
    acc = CalibrationAccumulator()
    acc.add_game(result)

    overall = acc.summary()
    hornets_view = acc.team_summary("HOR")
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# -----------------------------
# Per-game calibration records
# -----------------------------
@dataclass
class GameCalibrationInput:
    """
    Single game input for calibration between model output and reality.
    """

    home_team: str
    away_team: str

    # Model outputs at the time of the bet / prediction
    predicted_spread: float     # model line: home_team - away_team
    predicted_total: float      # model total points

    # Real final scores
    actual_home_score: int
    actual_away_score: int

    # Optional metadata
    context: str = "calibration"   # e.g., "calibration", "real_bet"
    tag: Optional[str] = None      # user-defined tag: "open_night", "back_to_back", etc.
    notes: Optional[str] = None    # free text for human annotation


@dataclass
class GameCalibrationResult:
    """
    Full calibration record for a finished game, including:
    - predicted lines
    - actual results
    - error metrics
    """

    home_team: str
    away_team: str

    predicted_spread: float
    predicted_total: float

    actual_home_score: int
    actual_away_score: int

    # Derived actual lines
    actual_spread: float     # home_score - away_score
    actual_total: float      # home_score + away_score

    # Errors (model - actual)
    spread_error: float      # positive = model more favorable to home than reality
    total_error: float       # positive = model higher total than reality

    # Absolute errors for MAE
    abs_spread_error: float
    abs_total_error: float

    # Metadata
    context: str = "calibration"
    tag: Optional[str] = None
    notes: Optional[str] = None


def compute_game_calibration(game: GameCalibrationInput) -> GameCalibrationResult:
    """
    Compute the calibration metrics for a single game.

    Returns a GameCalibrationResult that can be aggregated later.
    """
    actual_spread = float(game.actual_home_score - game.actual_away_score)
    actual_total = float(game.actual_home_score + game.actual_away_score)

    spread_error = float(game.predicted_spread - actual_spread)
    total_error = float(game.predicted_total - actual_total)

    return GameCalibrationResult(
        home_team=game.home_team,
        away_team=game.away_team,
        predicted_spread=float(game.predicted_spread),
        predicted_total=float(game.predicted_total),
        actual_home_score=int(game.actual_home_score),
        actual_away_score=int(game.actual_away_score),
        actual_spread=actual_spread,
        actual_total=actual_total,
        spread_error=spread_error,
        total_error=total_error,
        abs_spread_error=abs(spread_error),
        abs_total_error=abs(total_error),
        context=game.context,
        tag=game.tag,
        notes=game.notes,
    )


# -----------------------------
# Aggregation / tracking
# -----------------------------
@dataclass
class CalibrationAccumulator:
    """
    Holds many GameCalibrationResult entries and provides summary stats.

    This object is intentionally simple and in-memory only.
    Persistence (saving/loading to disk, CSV, etc.) is handled elsewhere.
    """

    games: List[GameCalibrationResult] = field(default_factory=list)

    def add_game(self, result: GameCalibrationResult) -> None:
        """Add a single game calibration record."""
        self.games.append(result)

    # ----- Core helpers -----
    def _filtered_games(
        self,
        team: Optional[str] = None,
        context: Optional[str] = None,
    ) -> List[GameCalibrationResult]:
        """
        Internal filter:
        - team: include games where team is home OR away (if provided)
        - context: match context exactly if provided
        """
        out: List[GameCalibrationResult] = []
        for g in self.games:
            if team is not None and team not in (g.home_team, g.away_team):
                continue
            if context is not None and g.context != context:
                continue
            out.append(g)
        return out

    def _summary_from_games(self, games: List[GameCalibrationResult]) -> Dict[str, float]:
        """Compute summary stats from a list of games."""
        if not games:
            return {
                "count": 0,
                "avg_spread_error": 0.0,
                "avg_total_error": 0.0,
                "mae_spread": 0.0,
                "mae_total": 0.0,
            }

        n = float(len(games))
        sum_spread_error = sum(g.spread_error for g in games)
        sum_total_error = sum(g.total_error for g in games)
        sum_abs_spread = sum(g.abs_spread_error for g in games)
        sum_abs_total = sum(g.abs_total_error for g in games)

        return {
            "count": int(n),
            # Signed error (bias)
            "avg_spread_error": sum_spread_error / n,
            "avg_total_error": sum_total_error / n,
            # Mean absolute error (how far off on average)
            "mae_spread": sum_abs_spread / n,
            "mae_total": sum_abs_total / n,
        }

    # ----- Public summary APIs -----
    def summary(self, context: Optional[str] = None) -> Dict[str, float]:
        """
        Overall summary across all games (optionally filtered by context).

        Example:
            acc.summary()                      # all games
            acc.summary(context="real_bet")    # only real bets
        """
        games = self._filtered_games(team=None, context=context)
        return self._summary_from_games(games)

    def team_summary(self, team: str, context: Optional[str] = None) -> Dict[str, float]:
        """
        Summary for a specific team (either home or away).

        Example:
            acc.team_summary("HOR")
            acc.team_summary("DEN", context="real_bet")
        """
        games = self._filtered_games(team=team, context=context)
        return self._summary_from_games(games)

    def core_teams_summary(
        self,
        core_teams: Optional[List[str]] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Convenience helper to get summaries for a list of core teams.

        Example:
            acc.core_teams_summary(
                core_teams=["HOR", "NYK", "DET", "DEN", "OKC"],
                context="calibration",
            )
        """
        if core_teams is None:
            core_teams = []

        out: Dict[str, Dict[str, float]] = {}
        for code in core_teams:
            out[code] = self.team_summary(team=code, context=context)
        return out
