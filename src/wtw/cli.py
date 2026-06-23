from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import parse_commitments
from .report import render_report, write_jsonl
from .validation import read_jsonl, validate_snapshot

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_URL = "https://www.sec.gov/Archives/edgar/data/1045810/fixture-2026q2-8k.htm"
SNAPSHOTS_DIR = ROOT / "data" / "snapshots"


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
    for path in SNAPSHOTS_DIR.glob("*.jsonl"):
        validate_snapshot(path)


def latest_snapshot() -> Path | None:
    snapshots = sorted(SNAPSHOTS_DIR.glob("*.jsonl"))
    return snapshots[-1] if snapshots else None


def show_snapshot(path: Path) -> int:
    """Print a readable, ranked view of a committed snapshot. No args, read-only."""
    # ensure the em-dash and other unicode survive a non-utf-8 console (e.g. Windows cp1252)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = read_jsonl(path)
    if not rows:
        print(f"snapshot {path.name} has no edges")
        return 0
    # rank by quantity within flow kind is unit-incomparable, so rank by confidence
    # midpoint then quantity; disclosed (not inferred) outranks inferred.
    rows.sort(
        key=lambda r: (
            not r.get("inferred", False),
            (float(r["confidence_low"]) + float(r["confidence_high"])) / 2,
            float(r["quantity"]),
        ),
        reverse=True,
    )
    quarter = rows[0].get("quarter", path.stem)
    disclosed = sum(1 for r in rows if not r.get("inferred"))
    inferred = len(rows) - disclosed
    print(f"wafer-to-watt — accelerator commitment snapshot, {quarter}")
    print(
        f"{len(rows)} edge(s): {disclosed} disclosed, {inferred} inferred, "
        f"ranked disclosed-first by confidence then quantity\n"
    )
    header = (
        f"{'from':<10} {'to':<26} {'flow':<18} {'quantity':>9}  "
        f"{'unit':<26} {'conf':>11}  status"
    )
    print(header)
    print("-" * len(header))
    for r in rows:
        status = "inferred" if r.get("inferred") else "disclosed"
        print(
            f"{str(r.get('from_entity', '?'))[:10]:<10} "
            f"{str(r.get('to_entity', '?'))[:26]:<26} "
            f"{str(r.get('flow_kind', '?'))[:18]:<18} "
            f"{float(r.get('quantity', 0)):>9,.0f}  "
            f"{str(r.get('quantity_unit', '?'))[:26]:<26} "
            f"{float(r['confidence_low']):.2f}-{float(r['confidence_high']):.2f}  "
            f"{status}"
        )
    top = rows[0]
    print(
        f"\nstrongest edge: {top.get('from_entity')} -> {top.get('to_entity')} — "
        f"{float(top.get('quantity', 0)):,.0f} {top.get('quantity_unit')} "
        f"({'inferred' if top.get('inferred') else 'disclosed'}, "
        f"confidence {float(top['confidence_low']):.2f}-{float(top['confidence_high']):.2f}). "
        f"evidence: {top.get('evidence_url')}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wtw")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--quarter", default="2026q2")
    sub.add_parser("validate")
    show = sub.add_parser("show", help="print a readable ranked view of the latest snapshot")
    show.add_argument("--snapshot", default=None, help="path to a snapshot jsonl (default: latest)")
    args = parser.parse_args(argv)
    if args.command == "show":
        path = Path(args.snapshot) if args.snapshot else latest_snapshot()
        if path is None or not path.is_file():
            raise SystemExit("no snapshot found under data/snapshots/*.jsonl — run `build` first")
        return show_snapshot(path)
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

