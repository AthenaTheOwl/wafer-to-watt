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
import sys
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent
SNAPSHOTS = REPO / "data" / "snapshots"

# make the real engine importable: src/wtw is the package, drive it directly.
sys.path.insert(0, str(REPO / "src"))
from wtw.parser import paragraphs_from_text, parse_paragraphs  # noqa: E402
from wtw.validation import check_rows  # noqa: E402

FIXTURE_URL = "https://www.sec.gov/Archives/edgar/data/1045810/fixture-2026q2-8k.htm"

EXAMPLE_8K = """<html><body>
<p>NVIDIA disclosed 50000 GB200 systems for CloudCo AI Factory in this fixture paragraph.</p>
<p>AMD disclosed 18000 MI300 accelerators for ResearchGrid Compute in this fixture paragraph.</p>
<p>Broadcom disclosed 120000 custom accelerator wafers for Atlas Hyperscale; this edge is inferred from fixture capacity language.</p>
<p>Intel disclosed 9000 custom accelerator wafers for Public Sector Compute Reserve in this fixture paragraph.</p>
</body></html>"""


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

st.divider()

# ── interactive: drive the real parser + gate on your own 8-K text ──────────
st.subheader("parse + gate your own 8-K text")
st.caption(
    "paste 8-K-style commitment paragraphs below. the page runs the *real* engine "
    "(`wtw.parser.parse_paragraphs` then `wtw.validation.check_rows`) on your input — "
    "the same extraction and gate the build pipeline uses — and shows which edges it "
    "pulled out and whether they pass the snapshot gate, with the reason for each check. "
    "no lookup, no hardcoded answer."
)
st.caption(
    "each `<p>` paragraph is matched against: "
    "`<From> disclosed <qty> <GB200 systems|MI300 accelerators|custom accelerator wafers> "
    "for <To> in this fixture paragraph.` — add the word **inferred** to a paragraph to "
    "mark that edge inferred (the gate caps inferred edges at 30% of a snapshot)."
)

user_quarter = st.text_input("quarter label", value="2026q2")
user_html = st.text_area(
    "8-K paragraphs (html with <p> tags)",
    value=EXAMPLE_8K,
    height=220,
    help="pre-filled with the committed fixture — edit it, add/remove paragraphs, then re-run.",
)

if st.button("parse + validate", type="primary"):
    paragraphs = paragraphs_from_text(user_html)
    edges = parse_paragraphs(paragraphs, user_quarter.strip() or "adhoc", f"{FIXTURE_URL}")
    rows = [edge.to_dict() for edge in edges]

    pc1, pc2, pc3 = st.columns(3)
    pc1.metric("paragraphs", len(paragraphs))
    pc2.metric("edges extracted", len(edges))
    matched_inferred = sum(1 for r in rows if r.get("inferred"))
    pc3.metric("inferred", matched_inferred)

    if not edges:
        st.warning(
            "the real parser extracted 0 edges — no paragraph matched the commitment "
            "pattern. check the units (GB200 systems / MI300 accelerators / custom "
            "accelerator wafers) and the `... for <To> in this fixture paragraph.` ending."
        )
    else:
        st.markdown("**edges the real parser extracted from your text:**")
        st.dataframe(
            [
                {
                    "edge_id": r["edge_id"],
                    "from": r["from_entity"],
                    "to": r["to_entity"],
                    "flow": r["flow_kind"],
                    "quantity": r["quantity"],
                    "unit": r["quantity_unit"],
                    "confidence": f"{r['confidence_low']:.2f}-{r['confidence_high']:.2f}",
                    "status": "inferred" if r["inferred"] else "disclosed",
                }
                for r in rows
            ],
            use_container_width=True,
            hide_index=True,
        )

    # drive the real gate on the extracted rows
    results = check_rows(rows)
    passed_all = all(r["passed"] for r in results)
    if passed_all:
        st.success("GATE PASSED — this snapshot would be accepted by `validate_snapshot`.")
    else:
        st.error("GATE FAILED — `validate_snapshot` would reject this snapshot. see why below.")

    st.markdown("**gate checks (the real `check_rows` engine):**")
    st.dataframe(
        [
            {
                "check": r["check"],
                "result": "pass" if r["passed"] else "FAIL",
                "why": r["detail"],
            }
            for r in results
        ],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("raw extracted edges (jsonl, exactly what the gate saw)"):
        st.code("\n".join(json.dumps(r, sort_keys=True) for r in rows) or "(no edges)", language="json")

st.caption(
    "v0.1 ships one EDGAR fixture quarter. the parser, model, and validation live in "
    "`src/wtw/`; the snapshot view above reads the committed `data/snapshots/*.jsonl`, "
    "and the section below it drives those same `src/wtw/` functions live on your input. "
    "repo: github.com/AthenaTheOwl/wafer-to-watt"
)
