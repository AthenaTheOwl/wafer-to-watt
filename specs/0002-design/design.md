# design — 0002-design

## shape

The v0.1 path is intentionally fixture-first:

1. parse cached HTML paragraphs
2. extract commitment grammar matches
3. write commitment edges to JSONL
4. render a short allocation memo
5. validate schema shape and inferred-edge share

## non-goals

- network EDGAR fetch
- transcript ingestion
- entity resolution
- Cytoscape rendering

