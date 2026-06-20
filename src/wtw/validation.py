from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def validate_snapshot(path: Path) -> None:
    rows = read_jsonl(path)
    if not rows:
        raise ValueError(f"{path} has no rows")
    inferred = [row for row in rows if row.get("inferred") is True]
    if len(inferred) / len(rows) > 0.30:
        raise ValueError(f"{path} exceeds inferred-edge share limit")
    for row in rows:
        if not row.get("evidence_url"):
            raise ValueError(f"{row.get('edge_id')} missing evidence_url")
        if float(row["confidence_low"]) > float(row["confidence_high"]):
            raise ValueError(f"{row.get('edge_id')} has inverted confidence interval")

