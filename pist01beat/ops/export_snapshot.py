"""
pist01beat.ops.export_snapshot

Write a deterministic audited export snapshot to disk.
Infrastructure-only. Best-effort imports. No engine imports.
"""

from __future__ import annotations

import argparse
import os
from datetime import date
from typing import Any, Dict, List, Optional


EXPORT_SNAPSHOT_VERSION = "export_snapshot_v1_readonly"


def _safe_mkdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _best_effort_imports():
    cli_warnings: List[str] = []

    build_audited_export = None
    dumps = None
    dump_to_path = None

    try:
        from pist01beat.ops.export_cli import build_audited_export as _bae  # type: ignore
        build_audited_export = _bae
    except Exception:
        cli_warnings.append("missing_export_cli")

    try:
        from pist01beat.ops.json_deterministic import dumps as _d, dump_to_path as _dtp  # type: ignore
        dumps = _d
        dump_to_path = _dtp
    except Exception:
        cli_warnings.append("missing_json_deterministic")

    return build_audited_export, dumps, dump_to_path, cli_warnings


def write_export_snapshot(base_dir: str = "exports", snapshot_date: Optional[str] = None) -> dict:
    """
    Writes:
      <base_dir>/<YYYY-MM-DD>/export_audited.json
      <base_dir>/<YYYY-MM-DD>/summary.json

    Returns fixed keys:
    {
      "ok": bool,
      "snapshot_dir": str or None,
      "paths": {"export": str or None, "summary": str or None},
      "warnings": [..],
      "version": <EXPORT_SNAPSHOT_VERSION>
    }
    """
    warnings: List[str] = []

    build_audited_export, dumps, dump_to_path, w = _best_effort_imports()
    warnings.extend(w)

    d = snapshot_date or date.today().isoformat()
    snapshot_dir = os.path.join(base_dir, d)

    out: Dict[str, Any] = {}
    out["ok"] = False
    out["snapshot_dir"] = None
    out["paths"] = {"export": None, "summary": None}
    out["warnings"] = warnings
    out["version"] = EXPORT_SNAPSHOT_VERSION

    if build_audited_export is None:
        warnings.append("snapshot_failed_missing_export_cli")
        return out

    bundle = build_audited_export()

    _safe_mkdir(snapshot_dir)

    export_path = os.path.join(snapshot_dir, "export_audited.json")
    summary_path = os.path.join(snapshot_dir, "summary.json")

    # deterministic writer preferred
    if dump_to_path is not None and dumps is not None:
        dump_to_path(bundle, export_path)

        export_obj = bundle.get("export") if isinstance(bundle, dict) else None
        validation = bundle.get("validation") if isinstance(bundle, dict) else None
        export_hash = bundle.get("export_hash") if isinstance(bundle, dict) else None
        stamp = bundle.get("stamp") if isinstance(bundle, dict) else None
        cli_warnings = bundle.get("cli_warnings") if isinstance(bundle, dict) else None

        summary = {
            "export_version": export_obj.get("version") if isinstance(export_obj, dict) else None,
            "validation_ok": validation.get("ok") if isinstance(validation, dict) else None,
            "errors_n": len(validation.get("errors") or []) if isinstance(validation, dict) else None,
            "warnings_n": len(validation.get("warnings") or []) if isinstance(validation, dict) else None,
            "hash_prefix": export_hash[:12] if isinstance(export_hash, str) else None,
            "stamp_keys": sorted(list(stamp.keys())) if isinstance(stamp, dict) else None,
            "cli_warnings_n": len(cli_warnings) if isinstance(cli_warnings, list) else None,
            "snapshot_date": d,
        }
        dump_to_path(summary, summary_path)
    else:
        warnings.append("snapshot_failed_missing_json_deterministic")
        return out

    out["ok"] = True
    out["snapshot_dir"] = os.path.abspath(snapshot_dir)
    out["paths"] = {"export": os.path.abspath(export_path), "summary": os.path.abspath(summary_path)}
    return out


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="export_snapshot", add_help=True)
    p.add_argument("--base", type=str, default="exports", help="Base directory for snapshots.")
    p.add_argument("--date", type=str, default=None, help="Snapshot date folder (YYYY-MM-DD). Defaults to today.")
    p.add_argument("--print", dest="do_print", action="store_true", help="Print deterministic result JSON.")
    args = p.parse_args(argv)

    res = write_export_snapshot(base_dir=args.base, snapshot_date=args.date)

    if args.do_print:
        try:
            from pist01beat.ops.json_deterministic import dumps as _dumps  # type: ignore
            print(_dumps(res))
        except Exception:
            print(res)

    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
