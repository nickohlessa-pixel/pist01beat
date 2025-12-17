"""
pist01beat.ops.repo_guard

Repo root + layout guardrails to prevent "one directory too high" mistakes.
Infrastructure-only. No engine imports.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional


REPO_GUARD_VERSION = "repo_guard_v1_readonly"


def _is_repo_root(path: str) -> bool:
    return os.path.isdir(os.path.join(path, ".git"))


def detect_repo_root(start: str = ".") -> dict:
    """
    Walk upward from `start` to find a directory containing `.git`.

    Returns (best-effort, never raises):
    {
      "repo_root": <abs path or None>,
      "has_git": <bool>,
      "start": <abs start>,
      "expected": {
         "package_dir": <abs path>,
         "ops_dir": <abs path>,
         "pkg_init": <abs path>,
         "ops_init": <abs path>,
      },
      "exists": { ... bools ... },
      "warnings": [..],
      "version": <REPO_GUARD_VERSION>
    }
    """
    warnings: List[str] = []

    start_abs = os.path.abspath(start)
    cur = start_abs

    repo_root: Optional[str] = None
    while True:
        if _is_repo_root(cur):
            repo_root = cur
            break
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent

    has_git = repo_root is not None

    # Expected layout relative to repo root:
    # repo_root/pist01beat (package) and repo_root/pist01beat/ops (ops package)
    expected: Dict[str, Optional[str]] = {
        "package_dir": None,
        "ops_dir": None,
        "pkg_init": None,
        "ops_init": None,
    }
    exists: Dict[str, bool] = {
        "package_dir": False,
        "ops_dir": False,
        "pkg_init": False,
        "ops_init": False,
    }

    if not has_git:
        warnings.append("missing_git_repo_root")
    else:
        pkg_dir = os.path.join(repo_root, "pist01beat")
        ops_dir = os.path.join(pkg_dir, "ops")
        pkg_init = os.path.join(pkg_dir, "__init__.py")
        ops_init = os.path.join(ops_dir, "__init__.py")

        expected = {
            "package_dir": os.path.abspath(pkg_dir),
            "ops_dir": os.path.abspath(ops_dir),
            "pkg_init": os.path.abspath(pkg_init),
            "ops_init": os.path.abspath(ops_init),
        }

        exists = {
            "package_dir": os.path.isdir(pkg_dir),
            "ops_dir": os.path.isdir(ops_dir),
            "pkg_init": os.path.isfile(pkg_init),
            "ops_init": os.path.isfile(ops_init),
        }

        if not exists["package_dir"]:
            warnings.append("missing_package_dir")
        if not exists["ops_dir"]:
            warnings.append("missing_ops_dir")
        if not exists["pkg_init"]:
            warnings.append("missing_pkg_init")
        if not exists["ops_init"]:
            warnings.append("missing_ops_init")

    out: Dict[str, object] = {}
    out["repo_root"] = os.path.abspath(repo_root) if repo_root else None
    out["has_git"] = has_git
    out["start"] = start_abs
    out["expected"] = expected
    out["exists"] = exists
    out["warnings"] = warnings
    out["version"] = REPO_GUARD_VERSION
    return out


def assert_repo_layout(start: str = ".") -> None:
    """
    Raises RuntimeError with a clear message if:
    - no .git repo root found, or
    - expected package layout isn't present.
    """
    info = detect_repo_root(start=start)
    if not info.get("has_git"):
        raise RuntimeError("repo_guard: .git repo root not found from start=%r" % start)

    exists = info.get("exists") or {}
    warnings = info.get("warnings") or []
    if warnings:
        # Keep message short + actionable
        raise RuntimeError(
            "repo_guard: repo layout invalid. warnings=%s repo_root=%s"
            % (warnings, info.get("repo_root"))
        )
