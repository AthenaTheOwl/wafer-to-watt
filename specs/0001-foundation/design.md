# Design — 0001-foundation (wafer-to-watt)

## Shape

A quarterly batch tied to earnings season. Two extraction layers
(EDGAR filings and earnings transcripts) feed a commitments graph
builder. The builder reconciles overlapping disclosures into
deduped edges with confidence intervals. A render pass produces
the report, the PDF, and the Cytoscape JSON.

## Components

### Extraction (`src/extraction/`)

- `edgar_8k_parser.py` — fetches and parses 8-K filings from EDGAR
  for the configured ticker set. Extracts paragraphs that match the
  commitment grammar (purchase obligations, capacity commitments,
  multi-year contracts named to a specific accelerator family).
  Output: raw `Commitment` candidates per filing.
- `earnings_transcript.py` — parses earnings-call transcripts for
  the configured ticker set; extracts management quotes that name
  specific accelerator commitments, CoWoS share, HBM stack count.
  Output: raw `Commitment` candidates per transcript.
- `base.py` — declares the `Commitment` model and the
  `ExtractionAdapter` protocol.

### Graph (`src/graph/`)

- `commitments.py` — takes raw `Commitment` candidates and merges
  them into the commitments graph. Reconciles overlapping
  disclosures (same buyer, same vendor, same quarter, same flow)
  into one edge with widened confidence interval. Marks
  inferred edges where the extraction rule produced the value
  rather than the source.
- `entities.py` — entity-resolution layer that maps
  "NVIDIA Corporation", "NVDA", "Nvidia" to one canonical entity
  ID. Driven by a small checked-in alias table.

### Render (`src/render/`)

- `cytoscape_export.py` — emits the quarterly graph as Cytoscape
  JSON with the agreed color encoding for inferred vs disclosed
  edges.
- `report.py` — emits the quarterly markdown report from the
  snapshot parquet and a Jinja template.
- `pdf.py` — pandoc wrapper.

### Eval (`eval/`)

- `citation_faithfulness.py` — loads a hand-labeled validation set
  (`eval/validation_set.yaml`) and asserts every edge's evidence
  URL contains the claimed quantity within the cited paragraph.
  Reports a faithfulness score; fails if below 0.95.

## Data flow

```
EDGAR 8-Ks ----> edgar_8k_parser ---+
                                    |
transcripts --> earnings_transcript-+--> commitments.py
                                                 |
                                                 v
                                  data/snapshots/2026q3.parquet
                                                 |
                          +----------------------+---------------------+
                          v                      v                     v
                  cytoscape_export       render/report.py     eval/citation_faithfulness.py
                          |                      |
                          v                      v
              reports/2026q3.cytoscape.json  reports/2026q3-allocations.md
```

## Non-goals for 0001

- Tickers beyond the four named (NVDA, AVGO, AMD, INTC).
- Coverage of GPU-as-a-service spot pricing.
- A live tracker. Quarterly cadence only.
- Multi-language support; English filings only in v0.
