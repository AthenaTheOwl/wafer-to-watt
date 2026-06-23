# WaferToWatt

Quarterly snapshot mapping every disclosed accelerator commitment
(NVDA, AVGO, AMD, Intel) to known and inferred CoWoS share and HBM
stack count, via citation-faithful EDGAR extraction.

## What this is

CoWoS sold out into 2026. HBM is allocated through 2027. Anthropic,
OpenAI, xAI, and Meta are making multi-billion-dollar bets on the
same scarce silicon slots. Nobody publishes who got what in a
citation-faithful structured way. Sell-side notes paraphrase the
same channel checks; SemiAnalysis runs unstructured prose.

WaferToWatt is the structured ground-truth layer. Every public
accelerator commitment from 8-Ks and earnings transcripts gets
parsed into a typed graph with confidence intervals on each edge.
Every edge has a SEC URL anchor or earnings-transcript timestamp.
Quarterly publication, tied to earnings season.

Bucket: ai-infra. Category: ai-infra. Brand prefix: `WTW`.

## Who this is for

- Sell-side semis analysts at GS, MS, JPM as a ground-truth layer
  they can cite.
- AI-lab capacity planners.
- Corp-dev and strategy teams at AVGO, AMD, Intel.
- Sovereign AI program managers (UAE G42, Saudi HUMAIN, EU AI
  factories).

## Status


v0.1 shipped and runs end to end. The entry command `python wtw.py validate` runs. See `specs/0002-design/` for the v0.1 scope and `STATUS.md` (where present) for the current state and next-feature queue.

## How to run

Placeholder. Run commands will land in spec `0002-edgar-pipeline`.
The shape will be:

```powershell
uv sync
uv run wtw fetch 8k --tickers NVDA,AVGO,AMD,INTC --since 2026-04-01
uv run wtw extract commitments data/raw/edgar/
uv run wtw graph build --quarter 2026q3
uv run wtw render report --quarter 2026q3
uv run wtw eval citation-faithfulness
```

## Layout

```
wafer-to-watt/
  AGENTS.md
  LICENSE
  README.md
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
  src/
    extraction/         # edgar_8k_parser, earnings_transcript
    graph/              # commitments graph builder
    render/             # cytoscape_export, report template
  data/
    raw/                # cached EDGAR filings (gitignored)
    snapshots/          # 2026q3.parquet etc (checked in)
  reports/              # checked-in quarterly markdown + PDF
  eval/                 # citation_faithfulness.py
  decisions/            # DEC-WTW-* architectural choices
```

## Compounds with

- `chip-supply-chain-map` is the parent graph; this repo specializes
  to accelerator-commitment edges.
- GridSilicon for silicon-side vs grid-side fusion.
- FabRiskRADAR shares the evidence-pipeline pattern.

## License

MIT. See [LICENSE](LICENSE).
