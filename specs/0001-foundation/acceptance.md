# Acceptance — 0001-foundation (wafer-to-watt)

v0 is done when the following commands all succeed on a clean clone.

## Commands

```powershell
uv sync
uv run wtw fetch 8k --tickers NVDA,AVGO,AMD,INTC --since 2026-04-01 --cache tests/fixtures/edgar
uv run wtw extract commitments tests/fixtures/edgar/
uv run wtw extract transcripts tests/fixtures/transcripts/
uv run wtw graph build --quarter 2026q3
uv run wtw render report --quarter 2026q3
uv run wtw render pdf --quarter 2026q3
uv run wtw render cytoscape --quarter 2026q3
uv run python eval/citation_faithfulness.py
uv run pytest
uv run python scripts/validate_schemas.py
uv run python scripts/voice_lint.py
uv run python scripts/traceability.py
```

## Gates that must pass

- All tests pass under `pytest`.
- `validate_schemas.py` exits 0 against
  `data/snapshots/2026q3.parquet`.
- `traceability.py` exits 0: every edge has a non-empty
  `evidence_url`.
- `voice_lint.py` exits 0 against
  `reports/2026q3-allocations.md`.
- `citation_faithfulness.py` reports a faithfulness score >= 0.95
  on the hand-labeled validation set.
- No more than 30% of edges in the snapshot have `inferred=true`.

## Artifacts produced

- `data/snapshots/2026q3.parquet` validates against the commitment
  schema.
- `reports/2026q3-allocations.md` exists and lints clean.
- `reports/2026q3-allocations.pdf` is produced from the same snapshot.
- `reports/2026q3.cytoscape.json` validates as Cytoscape JSON and
  uses the agreed color encoding.
- `decisions/DEC-WTW-001-commitments-schema.md` and the two follow-up
  decision records are present and linked from the report.

## What v0 explicitly does not promise

- Coverage of tickers beyond the four named.
- Coverage of allocation deals not disclosed in SEC filings or public
  transcripts.
- A live tracker. Quarterly publication only.
- A REST API.
