# AGENTS.md — wafer-to-watt

Operating contract for AI agents (Claude, Codex, Cursor) working in
this repo. Conventions match the AthenaTheOwl portfolio so an agent
already trained on `supplier-risk-rag-agent` or
`chip-supply-chain-map` recognizes the shape.

## What this repo is

A quarterly publication tied to earnings season. The artifact is the
checked-in quarterly report under `reports/<quarter>-allocations.md`,
the PDF render, the snapshot parquet, and the Cytoscape JSON.
Every edge in the graph cites a public SEC filing or earnings
transcript by URL and timestamp.

## Voice constraints

- No marketing words. The banned set will live in
  `scripts/voice_lint.py::BANNED_FAIL` once the lint script lands in
  spec 0002. Examples that always fail: leverage, demonstrate, seamless,
  cutting-edge, best-in-class, synergy.
- No antithetical reversals as a structural device.
- Plain assertions. Quantities carry units and confidence intervals.
  No "industry sources say" without a URL.
- Inferred edges are labeled `inferred=true` in the data and "inferred"
  in the prose. Disclosed edges are labeled `inferred=false`.

## Gates

Will land in spec `0002-edgar-pipeline`. The intended chain:

- `voice_lint` on every report.
- `validate_schemas` on every commitments-graph snapshot.
- `citation_faithfulness`: every edge must have a SEC URL anchor or
  transcript timestamp; the eval must pass at >= 95% on the
  hand-labeled validation set.
- `traceability`: an edge whose evidence URL is unreachable for two
  consecutive runs is flagged for review.

## Out of scope

- Channel checks under NDA. Public SEC and transcript content only.
- Coverage of non-public allocation deals (no leaks, no rumors).
- Live tracking. Quarterly publication, tied to the earnings calendar.
- A REST API. Consumers read the parquet and the JSON directly.
