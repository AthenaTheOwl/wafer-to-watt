from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.wtw.parser import paragraphs_from_html, parse_commitments
from src.wtw.validation import read_jsonl, validate_snapshot

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "raw" / "edgar" / "2026q2_8k_fixture.html"


def test_parser_extracts_fixture_paragraphs() -> None:
    paragraphs = paragraphs_from_html(FIXTURE)
    assert len(paragraphs) == 4


def test_parser_emits_commitment_edges() -> None:
    edges = parse_commitments(FIXTURE, "2026q2", "https://www.sec.gov/Archives/fixture.htm")
    assert len(edges) == 4
    assert {edge.flow_kind for edge in edges} == {"accelerator_commit", "wafer_start"}
    assert sum(1 for edge in edges if edge.inferred) == 1
    assert {edge.to_entity for edge in edges} == {
        "CloudCo AI Factory",
        "ResearchGrid Compute",
        "Atlas Hyperscale",
        "Public Sector Compute Reserve",
    }


def test_cli_builds_snapshot_and_report() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "wtw", "build", "--quarter", "2026q2"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    snapshot = ROOT / payload["snapshot_path"]
    report = ROOT / payload["report_path"]
    assert snapshot.is_file()
    assert report.is_file()
    validate_snapshot(snapshot)


def test_inferred_share_gate() -> None:
    rows = read_jsonl(ROOT / "data" / "snapshots" / "2026q2.jsonl")
    assert sum(1 for row in rows if row["inferred"]) / len(rows) <= 0.30


def test_cli_show_prints_ranked_snapshot() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "wtw", "show"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    out = result.stdout
    assert "accelerator commitment snapshot" in out
    assert "4 edge(s)" in out
    assert "strongest edge:" in out
    # disclosed edges must rank above the single inferred one
    assert out.index("NVIDIA") < out.index("Broadcom")
