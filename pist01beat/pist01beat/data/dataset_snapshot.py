import json
import hashlib
from datetime import datetime
from typing import List, Dict


def compute_dataset_hash(rows: List[Dict]) -> str:
    """
    Produces a deterministic hash of the dataset content.
    """
    serialized = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def snapshot_dataset(rows: List[Dict], output_path: str) -> Dict:
    """
    Writes a snapshot JSON with metadata and returns the snapshot summary.
    """
    rows_sorted = sorted(
        rows,
        key=lambda r: (
            r["date"],
            r["home_team"],
            r["away_team"],
        ),
    )

    dataset_hash = compute_dataset_hash(rows_sorted)

    snapshot = {
        "metadata": {
            "row_count": len(rows_sorted),
            "snapshot_timestamp_utc": datetime.utcnow().isoformat(),
            "dataset_hash": dataset_hash,
        },
        "data": rows_sorted,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot["metadata"]
