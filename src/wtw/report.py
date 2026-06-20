from __future__ import annotations

import json
from pathlib import Path

from .models import CommitmentEdge


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def render_report(path: Path, edges: list[CommitmentEdge]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    inferred_count = sum(1 for edge in edges if edge.inferred)
    lines = [
        f"# WaferToWatt allocations - {edges[0].quarter}",
        "",
        "Fixture-backed accelerator commitment edges parsed from cached filing-style text.",
        "The report is a pipeline proof, not a live allocation claim.",
        "",
        "## edges",
        "",
    ]
    for edge in edges:
        marker = "inferred" if edge.inferred else "disclosed"
        lines.extend(
            [
                f"### {edge.edge_id}",
                "",
                f"- from: {edge.from_entity}",
                f"- to: {edge.to_entity}",
                f"- flow: {edge.flow_kind}",
                f"- quantity: {edge.quantity:g} {edge.quantity_unit}",
                f"- confidence: {edge.confidence_low:.2f}-{edge.confidence_high:.2f}",
                f"- status: {marker}",
                f"- evidence: {edge.evidence_url}",
                "",
            ]
        )
    lines.extend(
        [
            "## methodology",
            "",
            "The parser strips cached HTML paragraphs and extracts commitment grammar matches. "
            "Every edge must carry a URL anchor and confidence interval.",
            "",
            "## inferences and limits",
            "",
            f"Inferred edges: {inferred_count} of {len(edges)}. "
            "The v0.1 gate fails if inferred edges exceed 30 percent of a quarter.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

