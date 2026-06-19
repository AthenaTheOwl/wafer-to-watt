# Requirements — 0001-foundation (wafer-to-watt)

Brand prefix: `WTW`.

## Scope

The foundation spec names the EDGAR-side extraction pipeline, the
commitments-graph schema, the citation-faithfulness eval, and the
quarterly publication discipline.

## Requirements

- R-WTW-001: The repo publishes one quarterly snapshot at
  `data/snapshots/<quarter>.parquet` and one report at
  `reports/<quarter>-allocations.md` per quarter.
- R-WTW-002: Every row in the snapshot represents an edge in the
  commitments graph and has the fields `edge_id`, `from_entity`,
  `to_entity`, `flow_kind`
  (`accelerator_commit` | `cowos_share` | `hbm_stacks` | `wafer_start`),
  `quantity`, `quantity_unit`, `confidence_low`, `confidence_high`,
  `evidence_url`, `evidence_timestamp`, `inferred` (boolean).
- R-WTW-003: Every row has a non-empty `evidence_url`. URLs are
  either SEC EDGAR filing anchors (8-K, 10-K, 10-Q) or earnings-call
  transcript anchors with timestamp.
- R-WTW-004: The `citation_faithfulness.py` eval runs against a
  hand-labeled validation set of at least 50 edges and must pass at
  >= 95%. Failure blocks publication.
- R-WTW-005: Edges with `inferred=true` are marked as inferred in
  the prose and in the Cytoscape render. v0 does not allow more than
  30% of any quarter's edges to be inferred.
- R-WTW-006: The Cytoscape render uses the same color encoding for
  inferred vs disclosed edges across quarters. v0 declares the
  encoding in `DEC-WTW-002-cytoscape-encoding.md`.
- R-WTW-007: The 8-K parser respects SEC EDGAR rate limits and uses
  the User-Agent string the project declares.
- R-WTW-008: The earnings-transcript parser only reads transcripts
  the project has the license to read. v0 ships with one licensed
  provider documented in `DEC-WTW-003-transcript-source.md`.
- R-WTW-009: A `voice_lint` pass runs against every checked-in
  report.
- R-WTW-010: Decision records live under `decisions/DEC-WTW-NNN.md`.
  The first is `DEC-WTW-001-commitments-schema.md`.
- R-WTW-011: The quarterly report ends with a `## Methodology` and a
  `## Inferences and limits` section. The latter names which edges
  are inferred and the inference rule used.
- R-WTW-012: This repo does not call any private API or scraped
  source that violates a publisher's terms.
