"""wafer-to-watt — live demo (Streamlit Community Cloud).

Reads the committed snapshot under data/snapshots/*.jsonl and shows the
accelerator-commitment edges parsed from a cached EDGAR 8-K fixture: who
committed how much of which silicon to whom, with confidence intervals and a
SEC URL anchor on every edge. No network, no secrets — runs entirely off the
committed snapshot.

Deploy: Streamlit Community Cloud -> New app -> repo AthenaTheOwl/wafer-to-watt,
branch main, main file streamlit_app.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent
SNAPSHOTS = REPO / "data" / "snapshots"


def load_rows() -> tuple[list[dict], str]:
    files = sorted(SNAPSHOTS.glob("*.jsonl"))
    if not files:
        return [], ""
    latest = files[-1]
    rows = [
        json.loads(line)
        for line in latest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return rows, latest.stem


st.set_page_config(page_title="wafer-to-watt — accelerator commitments", layout="wide")
st.title("wafer-to-watt")
st.caption(
    "accelerator commitment edges parsed from a cached EDGAR 8-K fixture — who "
    "committed how much of which silicon to whom, each edge carrying a confidence "
    "interval and a SEC URL anchor. a pipeline proof, not a live allocation claim."
)

rows, quarter = load_rows()
if not rows:
    st.warning("no snapshot found under data/snapshots/*.jsonl — run `python -m wtw build` first")
    st.stop()

st.subheader(f"commitment snapshot — {quarter}")

disclosed = sum(1 for r in rows if not r.get("inferred"))
inferred = len(rows) - disclosed

c1, c2, c3 = st.columns(3)
c1.metric("edges", len(rows))
c2.metric("disclosed", disclosed)
c3.metric("inferred", inferred, help="must stay at or below 30% of a quarter")

flow_kinds = sorted({r.get("flow_kind", "?") for r in rows})
chosen = st.multiselect(
    "flow kinds",
    options=flow_kinds,
    default=flow_kinds,
    help="accelerator_commit = systems/accelerators; wafer_start = wafer allocation",
)

shown = [r for r in rows if r.get("flow_kind") in chosen]
# rank disclosed-first, then by confidence midpoint, then quantity
shown.sort(
    key=lambda r: (
        not r.get("inferred", False),
        (float(r["confidence_low"]) + float(r["confidence_high"])) / 2,
        float(r.get("quantity", 0)),
    ),
    reverse=True,
)

st.dataframe(
    [
        {
            "from": r.get("from_entity"),
            "to": r.get("to_entity"),
            "flow": r.get("flow_kind"),
            "quantity": r.get("quantity"),
            "unit": r.get("quantity_unit"),
            "confidence": f"{float(r['confidence_low']):.2f}-{float(r['confidence_high']):.2f}",
            "status": "inferred" if r.get("inferred") else "disclosed",
            "evidence": r.get("evidence_url"),
        }
        for r in shown
    ],
    use_container_width=True,
    hide_index=True,
)

if shown:
    top = shown[0]
    st.info(
        f"**strongest edge:** {top.get('from_entity')} -> {top.get('to_entity')} — "
        f"{float(top.get('quantity', 0)):,.0f} {top.get('quantity_unit')} "
        f"({'inferred' if top.get('inferred') else 'disclosed'}, "
        f"confidence {float(top['confidence_low']):.2f}-{float(top['confidence_high']):.2f}). "
        f"evidence: {top.get('evidence_url')}"
    )

st.caption(
    "v0.1 ships one EDGAR fixture quarter. the parser, model, and validation live in "
    "`src/wtw/`; this page reads the committed `data/snapshots/*.jsonl`. "
    "repo: github.com/AthenaTheOwl/wafer-to-watt"
)
