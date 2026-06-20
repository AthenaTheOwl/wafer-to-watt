from __future__ import annotations

import argparse
import json
from pathlib import Path

from .parser import parse_commitments
from .report import render_report, write_jsonl
from .validation import validate_snapshot

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_URL = "https://www.sec.gov/Archives/edgar/data/1045810/fixture-2026q2-8k.htm"


def build_snapshot(quarter: str) -> tuple[Path, Path]:
    fixture_path = ROOT / "data" / "raw" / "edgar" / f"{quarter}_8k_fixture.html"
    edges = parse_commitments(fixture_path, quarter, FIXTURE_URL)
    snapshot_path = ROOT / "data" / "snapshots" / f"{quarter}.jsonl"
    report_path = ROOT / "reports" / f"{quarter}-allocations.md"
    write_jsonl(snapshot_path, [edge.to_dict() for edge in edges])
    render_report(report_path, edges)
    validate_snapshot(snapshot_path)
    return snapshot_path, report_path


def validate_all() -> None:
    for path in (ROOT / "data" / "snapshots").glob("*.jsonl"):
        validate_snapshot(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wtw")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--quarter", default="2026q2")
    sub.add_parser("validate")
    args = parser.parse_args(argv)
    if args.command == "build":
        snapshot, report = build_snapshot(args.quarter)
        print(
            json.dumps(
                {
                    "snapshot_path": snapshot.relative_to(ROOT).as_posix(),
                    "report_path": report.relative_to(ROOT).as_posix(),
                },
                sort_keys=True,
            )
        )
        return 0
    validate_all()
    print("valid: snapshots")
    return 0

