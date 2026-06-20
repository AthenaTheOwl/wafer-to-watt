# requirements — 0002-design

## scope

v0.1 ships a fixture-backed quarterly commitment snapshot from cached
filing-style text. It proves the extraction, edge schema, inferred-edge
limit, and report loop before live EDGAR access.

## requirements

- R-WTW-013: `python -m wtw build --quarter 2026q2` writes a JSONL
  snapshot and markdown report.
- R-WTW-014: Every edge carries an evidence URL anchor and timestamp.
- R-WTW-015: Inferred edges are marked in data and prose.
- R-WTW-016: The inferred-edge share is capped at 30 percent.
- R-WTW-017: `python -m wtw validate`, schema validation, pytest, and
  ruff must pass.

