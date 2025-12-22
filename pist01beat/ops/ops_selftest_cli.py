
"""
Read-only ops self-test (in-process).

Goal:
- Minimal deterministic validation that ops tooling is importable and functioning
- No writes, no engine imports, no model authority
- Prints a single OK summary line (or raises on failure)

Checks:
- repo_snapshot: can build snapshot + fingerprint
- preflight: can build report + fingerprint present
- ops_index: can build index + has tools
"""

from __future__ import annotations

import argparse
from typing import List, Optional

from pist01beat.ops.repo_snapshot import build_repo_snapshot
from pist01beat.ops.preflight_cli import build_preflight_report
from pist01beat.ops.ops_index import build_ops_index

OPS_SELFTEST_CLI_VERSION = "ops_selftest_cli_v1_readonly"


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ops_selftest_cli",
        description="Read-only self-test for ops tooling (deterministic).",
    )
    p.add_argument("--repo-root", default=None, help="Repo root path. Default: auto-detect from CWD.")
    p.add_argument("--max-file-mb", type=int, default=25, help="Skip files larger than this size (MB). Default: 25.")
    p.add_argument("--follow-symlinks", action="store_true", help="Follow symlinks during walk (default: false).")
    p.add_argument("--version", action="store_true", help="Print CLI version and exit.")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(OPS_SELFTEST_CLI_VERSION)
        return 0

    # 1) Repo snapshot
    snap = build_repo_snapshot(
        repo_root=args.repo_root,
        max_file_mb=int(args.max_file_mb),
        follow_symlinks=bool(args.follow_symlinks),
    )
    fp = snap.get("repo_fingerprint_sha256")
    if not isinstance(fp, str) or len(fp) < 12:
        raise AssertionError("repo_snapshot_missing_fingerprint")

    files = snap.get("files", [])
    if not isinstance(files, list) or len(files) == 0:
        raise AssertionError("repo_snapshot_empty_files")

    # 2) Preflight report
    pre = build_preflight_report(
        repo_root=args.repo_root,
        max_file_mb=int(args.max_file_mb),
        follow_symlinks=bool(args.follow_symlinks),
        exclude_dir=None,
        exclude_file=None,
    )
    pfp = pre.get("repo_fingerprint_sha256")
    if pfp != fp:
        # In normal conditions these should match since both use build_repo_snapshot fingerprinting.
        raise AssertionError("preflight_fingerprint_mismatch")

    # 3) Ops index
    idx = build_ops_index()
    tools = idx.get("tools", [])
    if not isinstance(tools, list) or len(tools) == 0:
        raise AssertionError("ops_index_empty_tools")

    n_tools = len(tools)
    snap_warn = len(snap.get("warnings", []) or [])
    pre_warn = len(pre.get("warnings", []) or [])
    idx_warn = len(idx.get("warnings", []) or [])

    print(f"OK fp:{fp[:12]} files:{len(files)} tools:{n_tools} warn:{snap_warn + pre_warn + idx_warn}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
