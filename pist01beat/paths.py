# FILE: paths.py
"""
Centralized path definitions for Pist01 Beat v3.4.

These values allow all modules to refer to locations symbolically,
instead of hardcoding paths throughout the repo. This makes Colab
and GitHub usage far easier and prevents path breakage.
"""

import os

# Base project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Suggested internal structure (folders may be created later as needed)
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

# File-level defaults
DEFAULT_LOG_FILE = os.path.join(LOGS_DIR, "pist01beat.log")
DEFAULT_MODEL_STATE = os.path.join(EXPORTS_DIR, "model_state.json")

# Small helper function
def ensure_directories():
    """Creates the folder structure if it doesn't exist."""
    for d in [DATA_DIR, LOGS_DIR, CACHE_DIR, EXPORTS_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)


if __name__ == "__main__":
    ensure_directories()
    print("paths.py loaded and directories validated.")

