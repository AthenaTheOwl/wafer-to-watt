# wafer-to-watt

One edge says a vendor committed 50,000 accelerator systems to a buyer, on the record.
Another says a second vendor's 120,000 custom-accelerator wafers are inferred from
capacity language — nobody signed for them. wafer-to-watt is the ledger that keeps those
two kinds of claim in different columns.

Both edges come from the illustrative fixture v0.1 ships, not from real filings: the
vendors (Vendor A–D), buyers, quantities and evidence anchors in
`data/snapshots/2026q2.jsonl` are synthetic and are not real disclosures.

## What it does

CoWoS is sold out into 2026 and HBM is allocated through 2027, so the labs placing
multi-billion-dollar accelerator orders are all reaching for the same scarce silicon.
Who actually got which slots is buried in 8-Ks and earnings transcripts. Sell-side
notes paraphrase the same channel checks; the structured ground truth doesn't exist in
one place.

wafer-to-watt parses every public accelerator commitment into a typed graph: who is
buying what from whom, how much, and how sure we are. A disclosed edge carries an SEC
URL anchor. An inferred edge carries a lower confidence band and says so. The line
between a filing and a rumor is the whole product, so the schema refuses to let them
blur. v0.1 ships one illustrative fixture quarter as a checked-in snapshot; its edges
and anchors are synthetic placeholders, not real disclosures.

## Try it

The CLI has three verbs, all offline against a committed, synthetic 8-K-style fixture:

```powershell
python -m wtw show                  # ranked, readable view of the latest snapshot
python -m wtw build --quarter 2026q2  # re-parse the fixture -> snapshot + report
python -m wtw validate              # gate every snapshot (evidence anchors, inferred share)
```

`show` reads `data/snapshots/2026q2.jsonl` and prints the commitment edges ranked
disclosed-first by confidence then quantity, with a one-line headline naming the
strongest edge:

```
wafer-to-watt — accelerator commitment snapshot, 2026q2
illustrative fixture data: vendors, buyers, quantities and evidence anchors are synthetic, not real disclosures
4 edge(s): 3 disclosed, 1 inferred, ranked disclosed-first by confidence then quantity

from       to                         flow                quantity  unit                              conf  status
------------------------------------------------------------------------------------------------------------------
Vendor A   CloudCo AI Factory         accelerator_commit    50,000  GB200 systems              0.90-0.98  disclosed
Vendor B   ResearchGrid Compute       accelerator_commit    18,000  MI300 accelerators         0.90-0.98  disclosed
Vendor D   Public Sector Compute Rese wafer_start            9,000  custom accelerator wafers  0.90-0.98  disclosed
Vendor C   Atlas Hyperscale           wafer_start          120,000  custom accelerator wafers  0.70-0.88  inferred

strongest edge: Vendor A -> CloudCo AI Factory — 50,000 GB200 systems (disclosed, confidence 0.90-0.98). evidence: https://example.invalid/fixtures/edgar/2026q2_8k_fixture.html#p1
```

The disclosed rows sit at the top with their evidence anchors. The inferred row sits at
the bottom with a wider band, where it belongs.

## Live demo

An interactive card-by-card view of the same committed snapshot:

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

`streamlit_app.py` reads `data/snapshots/*.jsonl` directly (paths relative to the file,
no network, no secrets): title and caption, an illustrative-data banner for fixture
rows, edge / disclosed / inferred metrics, a flow-kind filter, a ranked edge table, and
a headline callout for the strongest edge.

Deploy on Streamlit Community Cloud -> New app -> repo `AthenaTheOwl/wafer-to-watt`,
branch `main`, main file `streamlit_app.py`.

<!-- live url: https://share.streamlit.io/... (fill in after first deploy) -->

## How it connects

- [chip-supply-chain-map](https://github.com/AthenaTheOwl/chip-supply-chain-map) is the
  parent graph; this repo narrows to the accelerator-commitment edges.
- [grid-silicon](https://github.com/AthenaTheOwl/grid-silicon) scores the grid side of
  the same demand curve — phantom megawatts where this counts phantom wafers.
- [fab-risk-radar](https://github.com/AthenaTheOwl/fab-risk-radar) shares the
  evidence-pipeline pattern: every edge anchored to a source or marked inferred.

## Layout

```
src/wtw/          parser, models, report, validation, cli
data/snapshots/   2026q2.jsonl — the one illustrative fixture quarter v0.1 ships
data/raw/         the synthetic 8-K fixture (other cached filings gitignored)
reports/          checked-in quarterly markdown
schemas/  specs/  decisions/  tests/  docs/
```

## Limitations

The extraction pass is not a general 8-K parser. `src/wtw/parser.py` uses the
`PATTERN` regex to extract one synthetic fixture sentence template:
`disclosed ... for ... in this fixture paragraph`, with fixed units and simple
entity names. Real 8-K prose uses varied verbs, passive constructions, tables,
legal names, and product names, so this regex would not extract those
commitments. The schema, validation, confidence-band, and report machinery are
real and independent of that fixture regex; generalized extraction is future
work.

## Method update

[October method update: Units and disclosure status define what can be aggregated](docs/commitment-units-and-status.md).

## License

MIT. See [LICENSE](LICENSE).
