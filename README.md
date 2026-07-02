# wafer-to-watt

Nvidia ships 50,000 GB200 systems to one buyer. Broadcom's 120,000 custom-accelerator
wafers, by contrast, are inferred from a channel check — nobody signed for them on the
record. wafer-to-watt is the ledger that keeps those two facts in different columns.

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
blur. v0.1 ships one quarter as a checked-in snapshot.

## Try it

The CLI has three verbs, all offline against a committed EDGAR 8-K fixture:

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
4 edge(s): 3 disclosed, 1 inferred, ranked disclosed-first by confidence then quantity

from       to                         flow                quantity  unit                              conf  status
------------------------------------------------------------------------------------------------------------------
NVIDIA     CloudCo AI Factory         accelerator_commit    50,000  GB200 systems              0.90-0.98  disclosed
AMD        ResearchGrid Compute       accelerator_commit    18,000  MI300 accelerators         0.90-0.98  disclosed
Intel      Public Sector Compute Rese wafer_start            9,000  custom accelerator wafers  0.90-0.98  disclosed
Broadcom   Atlas Hyperscale           wafer_start          120,000  custom accelerator wafers  0.70-0.88  inferred

strongest edge: NVIDIA -> CloudCo AI Factory — 50,000 GB200 systems (disclosed, confidence 0.90-0.98). evidence: https://www.sec.gov/Archives/edgar/data/1045810/fixture-2026q2-8k.htm#p1
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
no network, no secrets): title and caption, edge / disclosed / inferred metrics, a
flow-kind filter, a ranked edge table, and a headline callout for the strongest edge.

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
data/snapshots/   2026q2.jsonl — the one quarter v0.1 ships
data/raw/         cached EDGAR filings (gitignored)
reports/          checked-in quarterly markdown
schemas/  specs/  decisions/  tests/  docs/
```

## License

MIT. See [LICENSE](LICENSE).
