from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from src.wtw.cli import FIXTURE_URL
from src.wtw.parser import paragraphs_from_html, parse_commitments
from src.wtw.report import ILLUSTRATIVE_NOTE, render_report
from src.wtw.validation import check_rows, read_jsonl, validate_snapshot

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "raw" / "edgar" / "2026q2_8k_fixture.html"


def test_parser_extracts_fixture_paragraphs() -> None:
    paragraphs = paragraphs_from_html(FIXTURE)
    assert len(paragraphs) == 4


def test_parser_emits_commitment_edges() -> None:
    edges = parse_commitments(FIXTURE, "2026q2", FIXTURE_URL)
    assert len(edges) == 4
    assert {edge.flow_kind for edge in edges} == {"accelerator_commit", "wafer_start"}
    assert sum(1 for edge in edges if edge.inferred) == 1
    # the fixture is synthetic, so its vendors are fictional placeholders
    assert {edge.from_entity for edge in edges} == {
        "Vendor A",
        "Vendor B",
        "Vendor C",
        "Vendor D",
    }
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
    assert ILLUSTRATIVE_NOTE in out
    assert "4 edge(s)" in out
    # disclosed edges must rank above the single inferred one
    assert out.index("Vendor A") < out.index("Vendor C")
    # the three disclosed edges tie on confidence and their units differ, so
    # no raw quantity picks a winner: the tie is stated and each edge listed
    headline = out.split("strongest edge: ", 1)[1]
    assert headline.startswith("tie — 3 disclosed edges")
    for vendor in ("Vendor A", "Vendor B", "Vendor D"):
        assert f"  {vendor} -> " in headline
    assert "Vendor C" not in headline


def test_cli_show_labels_only_fixture_rows_illustrative(tmp_path: Path) -> None:
    rows = read_jsonl(ROOT / "data" / "snapshots" / "2026q2.jsonl")
    live = tmp_path / "live.jsonl"
    live.write_text(
        "".join(json.dumps({**row, "extraction_mode": "live"}) + "\n" for row in rows),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "wtw", "show", "--snapshot", str(live)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    assert ILLUSTRATIVE_NOTE not in result.stdout


def test_fixture_evidence_anchors_cannot_point_at_a_real_filing() -> None:
    # fixture edges are synthetic; an anchor under a real issuer's SEC path would
    # read as a citation of a real filing, so they use the reserved .invalid TLD
    for snapshot in sorted((ROOT / "data" / "snapshots").glob("*.jsonl")):
        for row in read_jsonl(snapshot):
            if row["extraction_mode"] == "fixture":
                host = urlparse(row["evidence_url"]).hostname or ""
                assert host.endswith(".invalid"), row["edge_id"]


def test_report_body_pins_status_quantity_and_confidence(tmp_path: Path) -> None:
    edges = parse_commitments(FIXTURE, "2026q2", FIXTURE_URL)
    report = tmp_path / "2026q2-allocations.md"
    render_report(report, edges)
    body = report.read_text(encoding="utf-8")
    # each per-edge section starts with "### <edge_id>"; slice one out so status
    # is pinned to a specific edge, not just present somewhere in the body
    blocks = {
        chunk.splitlines()[0].strip(): "### " + chunk
        for chunk in body.split("### ")[1:]
    }
    disclosed_block = blocks["wtw-2026q2-001"]  # Vendor A, disclosed
    inferred_block = blocks["wtw-2026q2-003"]  # Vendor C, inferred
    assert "- status: disclosed" in disclosed_block
    assert "- status: inferred" in inferred_block
    # a known quantity line and the disclosed confidence band
    assert "- quantity: 50000 GB200 systems" in disclosed_block
    assert "- confidence: 0.90-0.98" in disclosed_block
    # the synthetic rows are labeled before anything else in the report
    assert body.splitlines()[0].endswith("(illustrative fixture)")
    assert "**Illustrative fixture data.**" in body.split("## edges")[0]
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
    assert _check(results, "confidence interval well-formed in [0, 1]")["passed"] is False


def test_check_rows_flags_non_numeric_confidence() -> None:
    row = _row()
    del row["confidence_high"]
    results = check_rows([row])
    assert _check(results, "confidence interval well-formed in [0, 1]")["passed"] is False


def test_parser_stops_the_buyer_name_at_a_sentence_period() -> None:
    from src.wtw.parser import parse_paragraphs

    edges = parse_paragraphs(
        ["Vendor X disclosed 100 GB200 systems for Foo Corp."], "2026q2", FIXTURE_URL
    )
    assert [edge.to_entity for edge in edges] == ["Foo Corp"]


def test_not_inferred_does_not_mark_an_edge_inferred() -> None:
    from src.wtw.parser import parse_paragraphs

    text = "Vendor X disclosed 100 GB200 systems for Foo in this fixture paragraph; {}."
    disclosed = parse_paragraphs([text.format("not inferred")], "2026q2", FIXTURE_URL)
    inferred = parse_paragraphs([text.format("inferred from capacity")], "2026q2", FIXTURE_URL)
    assert [edge.inferred for edge in disclosed] == [False]
    assert [edge.inferred for edge in inferred] == [True]
