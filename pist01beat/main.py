# FILE: main.py

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any


# ============================================================
#  TEAM DATA — FULL STRUCTURE (BEST OPTION)
# ============================================================

TEAMS = {
    "HOR": {
        "identity": {
            "pace": 101,
            "offense": 110,
            "defense": 118
        },
        "chaos_profile": {
            "chaos_rate": 0.35,
            "foul_variance": 0.22
        },
        "volatility_profile": {
            "minutes_variance": 0.40,
            "injury_risk": 0.15
        }
    },

    "DEN": {
        "identity": {
            "pace": 98,
            "offense": 118,
            "defense": 112
        },
        "chaos_profile": {
            "chaos_rate": 0.10,
            "foul_variance": 0.08
        },
        "volatility_profile": {
            "minutes_variance": 0.15,
            "injury_risk": 0.05
        }
    }
}


# ============================================================
#  DATA STRUCTURES
# ============================================================

@dataclass
class PredictionResult:
    """Container for prediction output."""
    engine_version: str
    home_team: str
    away_team: str
    model_spread: float
    model_total: float
    confidence: str
    volatility_flag: str
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
#  MODEL BRAIN — ENGINE SECTIONS
# ============================================================

class IdentityEngine:
    """Reads team identity data and produces matchup identity metrics."""

    def run(self, home_team: str, away_team: str) -> Dict[str, Any]:
        home = TEAMS.get(home_team, {}).get("identity", {})
        away = TEAMS.get(away_team, {}).get("identity", {})

        home_score = (home.get("offense", 0) - home.get("defense", 0)) / 10
        away_score = (away.get("offense", 0) - away.get("defense", 0)) / 10

        return {
            "home_identity_score": home_score,
            "away_identity_score": away_score,
            "pace_avg": (home.get("pace", 0) + away.get("pace", 0)) / 2,
            "notes": "IdentityEngine processed full identity data."
        }


class ChaosEngine:
    """Processes chaos tendencies based on team profiles."""

    def run(self, home_team: str, away_team: str) -> Dict[str, Any]:
        home = TEAMS.get(home_team, {}).get("chaos_profile", {})
        away = TEAMS.get(away_team, {}).get("chaos_profile", {})

        chaos_prob = (home.get("chaos_rate", 0) + away.get("chaos_rate", 0)) / 2
        foul_variance = (home.get("foul_variance", 0) + away.get("foul_variance", 0)) / 2

        chaos_flag = "high" if chaos_prob > 0.30 else "medium" if chaos_prob > 0.15 else "low"

        return {
            "chaos_prob": chaos_prob,
            "foul_variance": foul_variance,
            "chaos_flag": chaos_flag,
            "notes": "ChaosEngine processed chaos profiles."
        }


class VolatilityEngine:
    """Processes volatility based on chaos + identity + team volatility profiles."""

    def run(self, home_team: str, away_team: str,
            identity_data: Dict[str, Any], chaos_data: Dict[str, Any]) -> Dict[str, Any]:

        home = TEAMS.get(home_team, {}).get("volatility_profile", {})
        away = TEAMS.get(away_team, {}).get("volatility_profile", {})

        minutes_var = (home.get("minutes_variance", 0) + away.get("minutes_variance", 0)) / 2
        injury_risk = (home.get("injury_risk", 0) + away.get("injury_risk", 0)) / 2

        volatility_score = minutes_var * 0.6 + injury_risk * 0.4 + chaos_data["chaos_prob"] * 0.5

        volatility_flag = (
            "high" if volatility_score > 0.45 else
            "medium" if volatility_score > 0.25 else
            "low"
        )

        return {
            "volatility_score": volatility_score,
            "volatility_flag": volatility_flag,
            "notes": "VolatilityEngine processed volatility + chaos + identity."
        }


class IntegrationLayer:
    """Combines all engines to produce final prediction."""

    def integrate(self, identity_data: Dict[str, Any], chaos_data: Dict[str, Any],
                  vol_data: Dict[str, Any]) -> Dict[str, Any]:

        # Spread logic (placeholder math using real engine inputs)
        base_spread = (
            identity_data["home_identity_score"]
            - identity_data["away_identity_score"]
        )

        chaos_penalty = chaos_data["chaos_prob"] * 2
        volatility_penalty = vol_data["volatility_score"] * 3

        model_spread = round(base_spread - chaos_penalty - volatility_penalty, 2)

        # Total logic (based on pace)
        model_total = round(identity_data["pace_avg"] * 2.2 + chaos_data["foul_variance"] * 15, 2)

        confidence = (
            "low" if vol_data["volatility_flag"] == "high"
            else "medium" if vol_data["volatility_flag"] == "medium"
            else "high"
        )

        return {
            "model_spread": model_spread,
            "model_total": model_total,
            "confidence": confidence,
            "notes": "IntegrationLayer combined all engine outputs."
        }


# ============================================================
#  MAIN MODEL CLASS
# ============================================================

class Pist01Beat:
    """Full structured model skeleton with real data flow."""

    def __init__(self, version: str = "3.4-structured-skeleton-V2") -> None:
        self.version = version

        self.identity_engine = IdentityEngine()
        self.chaos_engine = ChaosEngine()
        self.volatility_engine = VolatilityEngine()
        self.integration_layer = IntegrationLayer()

    def predict(self, home_team: str, away_team: str) -> Dict[str, Any]:
        identity_data = self.identity_engine.run(home_team, away_team)
        chaos_data = self.chaos_engine.run(home_team, away_team)
        vol_data = self.volatility_engine.run(home_team, away_team, identity_data, chaos_data)
        integrated = self.integration_layer.integrate(identity_data, chaos_data, vol_data)

        result = PredictionResult(
            engine_version=self.version,
            home_team=home_team,
            away_team=away_team,
            model_spread=integrated["model_spread"],
            model_total=integrated["model_total"],
            confidence=integrated["confidence"],
            volatility_flag=vol_data["volatility_flag"],
            notes="Structured model executed."
        )

        return result.to_dict()


# ============================================================
#  DEMO HARNESS
# ============================================================

def _demo() -> None:
    model = Pist01Beat()
    result = model.predict("HOR", "DEN")

    print("✅ Structured Model (Phase 0c) executed successfully.")
    print("Prediction result:")
    print(result)


if __name__ == "__main__":
    _demo()
