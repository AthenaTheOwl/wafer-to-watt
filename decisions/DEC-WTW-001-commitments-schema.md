---
id: DEC-WTW-001-commitments-schema
spec: specs/0002-design/
requirement: R-WTW-014
date: 2026-06-20
status: approved
reversible: true
decision: |
  Store each disclosed or inferred accelerator commitment as one typed edge
  with a citation anchor, confidence interval, and inferred flag.
alternatives:
  - label: store prose notes only
    rejected_because: |
      Prose cannot be validated for evidence anchors or inferred-edge share.
  - label: wait for parquet output
    rejected_because: |
      JSONL is enough for the first reader-facing snapshot and keeps the
      fixture review simple.
rationale: |
  The edge schema is small enough to inspect by eye and strict enough to catch
  missing citations before a report ships.
evidence:
  - kind: spec
    ref: specs/0002-design/
rollback: |
  Replace the JSONL snapshot with parquet after the schema is stable; keep the
  same field names so old reports remain readable.
---

