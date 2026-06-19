# Tasks — 0001-foundation (wafer-to-watt)

Ordered for the first two to three PRs after this scaffold lands.

## PR 1 — EDGAR fetch plus 8-K parser

- [ ] Add `pyproject.toml` with `httpx`, `lxml`, `polars`, `pyarrow`, `pydantic`, `jsonschema`, `jinja2`, `pytest`, `ruff`.
- [ ] Add `schemas/commitment.schema.json`.
- [ ] Add `schemas/entity.schema.json`.
- [ ] Add `src/wtw/extraction/base.py` declaring the `Commitment` model.
- [ ] Add `src/wtw/extraction/edgar_8k_parser.py` with rate-limit-respecting fetch.
- [ ] Add `tests/fixtures/edgar/nvda_2026q2_8k.html` (cached real filing).
- [ ] Add `tests/test_edgar_8k_parser.py`.
- [ ] Add `scripts/validate_schemas.py`.
- [ ] Add `decisions/DEC-WTW-001-commitments-schema.md`.

## PR 2 — transcripts plus graph builder

- [ ] Add `src/wtw/extraction/earnings_transcript.py` reading from a fixture transcript file.
- [ ] Add `src/wtw/graph/entities.py` plus `data/entities.yaml` alias table.
- [ ] Add `src/wtw/graph/commitments.py` with merge-and-widen reconciliation.
- [ ] Add `tests/test_entities.py`.
- [ ] Add `tests/test_commitments_merge.py` covering the merge behavior.
- [ ] Add `decisions/DEC-WTW-002-cytoscape-encoding.md`.
- [ ] Add `decisions/DEC-WTW-003-transcript-source.md`.

## PR 3 — first report plus citation-faithfulness eval

- [ ] Add `src/wtw/render/report.py` plus the Jinja template.
- [ ] Add `src/wtw/render/pdf.py`.
- [ ] Add `src/wtw/render/cytoscape_export.py`.
- [ ] Add `reports/2026q3-allocations.md`.
- [ ] Add `eval/validation_set.yaml` (50 hand-labeled edges).
- [ ] Add `eval/citation_faithfulness.py`.
- [ ] Add `scripts/voice_lint.py` and wire as gate.
- [ ] Add `scripts/traceability.py` enforcing the evidence-URL rule.
