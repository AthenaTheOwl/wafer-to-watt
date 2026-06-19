# First PR — wafer-to-watt

The literal first PR after the scaffold. Narrow scope: the EDGAR
fetch path, the 8-K parser, and the commitment schema.

## Title

`feat(WTW): EDGAR 8-K parser plus commitments schema (PR 1)`

## Goal

Land the rate-limit-respecting EDGAR fetcher, the 8-K parser that
extracts commitment candidates, and the JSON Schema that constrains
the rest of the pipeline.

## Files added

- `pyproject.toml` — deps: `httpx`, `lxml`, `polars`, `pyarrow`,
  `pydantic`, `jsonschema`, `jinja2`, `pytest`, `ruff`.
- `src/wtw/__init__.py`
- `src/wtw/extraction/__init__.py`
- `src/wtw/extraction/base.py` — pydantic `Commitment` model and
  the `ExtractionAdapter` protocol.
- `src/wtw/extraction/edgar_8k_parser.py` — `httpx` client with the
  declared User-Agent and a token-bucket rate limit; lxml-based
  paragraph extraction; commitment-grammar pattern set.
- `schemas/commitment.schema.json` — v0 edge row shape.
- `schemas/entity.schema.json` — canonical entity row shape.
- `tests/fixtures/edgar/nvda_2026q2_8k.html` — a real cached NVDA
  8-K filing; small enough to commit, large enough to exercise the
  parser's paragraph-extraction path.
- `tests/test_edgar_8k_parser.py` — runs the parser on the fixture,
  asserts the expected commitment candidates are emitted and that
  each candidate carries a `source_url` anchored to the fixture.
- `tests/test_schemas_self.py` — validates each schema against
  JSON Schema 2020-12.
- `scripts/validate_schemas.py` — walks `schemas/` plus any
  `data/snapshots/*.parquet` and exits 1 on mismatch.
- `decisions/DEC-WTW-001-commitments-schema.md` — names the v0
  edge shape and the alternatives that were rejected.

## Files not in this PR

- Earnings transcript parser. PR 2.
- Entity resolution. PR 2.
- The graph builder. PR 2.
- The first report. PR 3.
- The Cytoscape renderer. PR 3.
- The citation-faithfulness eval. PR 3.
- Any CI workflow.

## Verification

Reviewer runs:

```powershell
uv sync
uv run pytest
uv run python scripts/validate_schemas.py
```

Expected: all tests pass; `validate_schemas.py` exits 0.

## Review checklist

- [ ] The EDGAR client sets a SEC-compliant `User-Agent`.
- [ ] The rate limit is configurable and defaults to under
      10 requests per second.
- [ ] No network call runs in `pytest`; the fixture file is used.
- [ ] Both schemas declare `$id` and `$schema`.
- [ ] No marketing words in any added markdown.

## After merge

PR 2 lands the transcript parser, the entity-resolution layer, and
the graph builder with merge-and-widen reconciliation. PR 3 ships
the first quarterly report at `reports/2026q3-allocations.md`, the
PDF, the Cytoscape JSON, and the citation-faithfulness eval.
