from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.wtw.parser import paragraphs_from_html, parse_commitments
from src.wtw.report import render_report
from src.wtw.validation import check_rows, read_jsonl, validate_snapshot

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
    by_to = {edge.to_entity: edge for edge in edges}
    # pin extracted quantities so a scaled/doubled value fails
    assert by_to["CloudCo AI Factory"].quantity == 50000.0
    assert by_to["ResearchGrid Compute"].quantity == 18000.0
    assert by_to["Atlas Hyperscale"].quantity == 120000.0
    assert by_to["Public Sector Compute Reserve"].quantity == 9000.0
    # pin confidence bands: disclosed 0.90-0.98, inferred 0.70-0.88
    disclosed = by_to["CloudCo AI Factory"]
    assert disclosed.inferred is False
    assert disclosed.confidence_low == 0.90
    assert disclosed.confidence_high == 0.98
    inferred_edge = by_to["Atlas Hyperscale"]
    assert inferred_edge.inferred is True
    assert inferred_edge.confidence_low == 0.70
    assert inferred_edge.confidence_high == 0.88


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


def test_report_body_pins_status_quantity_and_confidence(tmp_path: Path) -> None:
    edges = parse_commitments(FIXTURE, "2026q2", "https://www.sec.gov/Archives/fixture.htm")
    report = tmp_path / "2026q2-allocations.md"
    render_report(report, edges)
    body = report.read_text(encoding="utf-8")
    # each per-edge section starts with "### <edge_id>"; slice one out so status
    # is pinned to a specific edge, not just present somewhere in the body
    blocks = {
        chunk.splitlines()[0].strip(): "### " + chunk
        for chunk in body.split("### ")[1:]
    }
    disclosed_block = blocks["wtw-2026q2-001"]  # NVIDIA, disclosed
    inferred_block = blocks["wtw-2026q2-003"]  # Broadcom, inferred
    assert "- status: disclosed" in disclosed_block
    assert "- status: inferred" in inferred_block
    # a known quantity line and the disclosed confidence band
    assert "- quantity: 50000 GB200 systems" in disclosed_block
    assert "- confidence: 0.90-0.98" in disclosed_block
    # the inferred-count summary line
    assert "Inferred edges: 1 of 4." in body


def _row(**overrides: object) -> dict[str, object]:
    row = {
        "edge_id": "wtw-test-001",
        "inferred": False,
        "evidence_url": "https://example.test/e#p1",
        "confidence_low": 0.90,
        "confidence_high": 0.98,
    }
    row.update(overrides)
    return row


def _check(results: list[dict[str, object]], name: str) -> dict[str, object]:
    return next(r for r in results if r["check"] == name)


def test_check_rows_flags_missing_evidence_url() -> None:
    results = check_rows([_row(edge_id="ok"), _row(edge_id="bad", evidence_url="")])
    assert _check(results, "every edge has evidence_url")["passed"] is False


def test_check_rows_flags_inverted_confidence() -> None:
    results = check_rows([_row(confidence_low=0.99, confidence_high=0.80)])
    assert _check(results, "confidence interval not inverted")["passed"] is False


def test_check_rows_flags_non_numeric_confidence() -> None:
    row = _row()
    del row["confidence_high"]
    results = check_rows([row])
    assert _check(results, "confidence interval not inverted")["passed"] is False
