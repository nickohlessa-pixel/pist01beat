"""
Repo Snapshot CLI (read-only)

Usage:
  python -m pist01beat.ops repo-snapshot [--json] [--pretty] [--edge-slots PATH]

Purpose:
- Emit a deterministic snapshot of the repo state
- Optionally include a hash of a validated Edge Slots payload

Design:
- Infrastructure-only
- Deterministic
- No writes
- Stdlib only
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from pist01beat.ops.util_hash import sha256_text


def main(argv: List[str] | None = None) -> int:
    args = list(argv) if argv is not None else sys.argv[1:]

    want_json = "--json" in args
    want_pretty = "--pretty" in args

    snapshot: Dict[str, Any] = {
        "tool": "repo-snapshot",
    }

    # --- optional edge slots payload ---
    if "--edge-slots" in args:
        idx = args.index("--edge-slots")
        try:
            edge_path = Path(args[idx + 1])
        except IndexError:
            print("--edge-slots requires a path", file=sys.stderr)
            return 2

        from pist01beat.ops.edge_slots_schema import validate_edge_slots

        try:
            raw = edge_path.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except Exception as e:
            print(f"Failed to read edge slots JSON: {e}", file=sys.stderr)
            return 2

        try:
            norm = validate_edge_slots(payload)
        except Exception as e:
            print(f"Edge slots validation failed: {e}", file=sys.stderr)
            return 1

        edge_hash = sha256_text(
            json.dumps(norm, sort_keys=True, separators=(",", ":"))
        )

        snapshot["edge_slots"] = {
            "schema_version": norm["version"],
            "payload_hash": edge_hash,
            "path": str(edge_path),
        }

    # --- output ---
    if want_json:
        if want_pretty:
            print(json.dumps(snapshot, indent=2, sort_keys=True))
        else:
            print(json.dumps(snapshot, sort_keys=True))
    else:
        print(snapshot)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
