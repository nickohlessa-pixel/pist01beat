# FILE: config.py
"""
Static configuration module for Pist01 Beat v3.4.

This file defines:
- Global model version tag
- Baseline team profile parameters for core teams and a generic fallback
- Global spread/total baselines
- Chaos and volatility threshold values

All values here are intended as tunable knobs for the Pist01 Beat ecosystem.
They are read by the higher-level engines but contain no business logic themselves.
"""

# ============================================================
# MODEL METADATA
# ============================================================

MODEL_VERSION = "3.4-BaseConfig"

# ============================================================
# TEAM PROFILES
# ============================================================
# Notes:
# - base_power: overall team strength anchor (0–10 scale)
# - offense: offensive strength (0–10)
# - defense: defensive strength (0–10)
# - pace: tempo tendency (0–10; higher = faster)
# - chaos: structural weirdness / unpredictability (0–10)
# - volatility: game-to-game swinginess (0–10)


TEAM_PROFILES = {
    "HOR": {
        "name": "Charlotte Hornets",
        "base_power": 5.0,
        "offense": 5.5,
        "defense": 4.0,
        "pace": 6.8,
        "chaos": 7.2,
        "volatility": 7.5,
    },
    "DEN": {
        "name": "Denver Nuggets",
        "base_power": 9.0,
        "offense": 8.8,
        "defense": 7.8,
        "pace": 5.4,
        "chaos": 3.2,
        "volatility": 3.8,
    },
    "NYK": {
        "name": "New York Knicks",
        "base_power": 7.5,
        "offense": 7.0,
        "defense": 7.8,
        "pace": 4.8,
        "chaos": 4.0,
        "volatility": 4.5,
    },
    "DET": {
        "name": "Detroit Pistons",
        "base_power": 4.0,
        "offense": 4.3,
        "defense": 4.2,
        "pace": 6.0,
        "chaos": 6.5,
        "volatility": 6.8,
    },
    "OKC": {
        "name": "Oklahoma City Thunder",
        "base_power": 8.2,
        "offense": 8.4,
        "defense": 7.2,
        "pace": 7.0,
        "chaos": 5.2,
        "volatility": 5.8,
    },
    "GENERIC": {
        "name": "Generic Team",
        "base_power": 6.0,
        "offense": 6.0,
        "defense": 6.0,
        "pace": 5.5,
        "chaos": 5.0,
        "volatility": 5.0,
    },
}

# ============================================================
# SPREAD / TOTAL BASELINES
# ============================================================
# These values are global dials. They do NOT encode team-specific logic.


SPREAD_TOTAL_BASELINES = {
    # Baseline total for a neutral matchup before pace/power adjustments.
    "default_total": 225.0,
    # Default home-court edge (points added to home spread).
    "home_edge": 2.5,
    # How much pace delta (home pace - away pace) moves the spread.
    "pace_spread_scale": 0.10,
    # How much combined pace level shifts the game total.
    "pace_total_scale": 1.25,
    # How much base_power delta (home - away) moves the spread.
    "power_spread_scale": 0.60,
}

# ============================================================
# CHAOS / VOLATILITY THRESHOLDS
# ============================================================
# Values are on the 0–10 scales defined above.


CHAOS_VOLATILITY_THRESHOLDS = {
    "chaos_low": 3.5,
    "chaos_high": 6.5,
    "vol_low": 3.5,
    "vol_high": 6.5,
}


if __name__ == "__main__":
    # Minimal sanity check so this file can be executed standalone.
    print(f"Pist01 Beat Config Loaded — MODEL_VERSION={MODEL_VERSION}")
    print(f"Teams configured: {', '.join(TEAM_PROFILES.keys())}")
