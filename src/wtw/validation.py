from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for n, line in enumerate(handle, start=1):
            if line.strip():
                # a snapshot arg can point at any file; surface the line so a
                # non-JSONL input fails with a locatable message, not a traceback.
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as err:
                    raise ValueError(f"{path}: not valid JSONL at line {n}") from err
    return rows


INFERRED_SHARE_LIMIT = 0.30


def check_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run the snapshot gate over in-memory rows and return per-check results.

    This is the real validation engine, decomposed so both the raising
    validate_snapshot and the live Streamlit form can drive the same checks and
    explain *why* a snapshot passes or fails. Each result is
    {check, passed, detail}.
    """
    results: list[dict[str, Any]] = []

    if not rows:
        results.append({"check": "non-empty", "passed": False, "detail": "snapshot has no rows"})
        return results
    results.append(
        {"check": "non-empty", "passed": True, "detail": f"{len(rows)} edge(s) present"}
    )

    inferred = [row for row in rows if row.get("inferred") is True]
    share = len(inferred) / len(rows)
    results.append(
        {
            "check": "inferred-share <= 30%",
            "passed": share <= INFERRED_SHARE_LIMIT,
            "detail": f"{len(inferred)}/{len(rows)} inferred = {share:.0%} (limit {INFERRED_SHARE_LIMIT:.0%})",
        }
    )

    missing = [str(r.get("edge_id") or "?") for r in rows if not r.get("evidence_url")]
    results.append(
        {
            "check": "every edge has evidence_url",
            "passed": not missing,
            "detail": "all edges anchored to an evidence url"
            if not missing
            else f"missing on: {', '.join(missing)}",
        }
    )

    inverted: list[str] = []
    for row in rows:
        try:
            if float(row["confidence_low"]) > float(row["confidence_high"]):
                inverted.append(str(row.get("edge_id") or "?"))
        except (KeyError, TypeError, ValueError):
            inverted.append(str(row.get("edge_id") or "?"))
    results.append(
        {
            "check": "confidence interval not inverted",
            "passed": not inverted,
            "detail": "all intervals well-formed (low <= high)"
            if not inverted
            else f"inverted/malformed on: {', '.join(inverted)}",
        }
    )

    return results


def validate_snapshot(path: Path) -> None:
    rows = read_jsonl(path)
    for result in check_rows(rows):
        if not result["passed"]:
            raise ValueError(f"{path}: {result['check']} failed — {result['detail']}")

