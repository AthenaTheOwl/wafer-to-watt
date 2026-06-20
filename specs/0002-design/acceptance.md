# acceptance — 0002-design

Accepted when:

- `python -m wtw build --quarter 2026q2` writes `data/snapshots/2026q2.jsonl`.
- `reports/2026q2-allocations.md` lists every edge and labels inferred edges.
- `python -m wtw validate` passes.
- `python scripts/validate_schemas.py` passes.
- `python -m pytest tests/ -q` passes.

