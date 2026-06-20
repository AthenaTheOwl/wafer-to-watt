# WaferToWatt allocations - 2026q2

Fixture-backed accelerator commitment edges parsed from cached filing-style text.
The report is a pipeline proof, not a live allocation claim.

## edges

### wtw-2026q2-001

- from: NVIDIA
- to: CloudCo AI Factory
- flow: accelerator_commit
- quantity: 50000 GB200 systems
- confidence: 0.90-0.98
- status: disclosed
- evidence: https://www.sec.gov/Archives/edgar/data/1045810/fixture-2026q2-8k.htm#p1

### wtw-2026q2-002

- from: AMD
- to: ResearchGrid Compute
- flow: accelerator_commit
- quantity: 18000 MI300 accelerators
- confidence: 0.90-0.98
- status: disclosed
- evidence: https://www.sec.gov/Archives/edgar/data/1045810/fixture-2026q2-8k.htm#p2

### wtw-2026q2-003

- from: Broadcom
- to: Atlas Hyperscale
- flow: wafer_start
- quantity: 120000 custom accelerator wafers
- confidence: 0.70-0.88
- status: inferred
- evidence: https://www.sec.gov/Archives/edgar/data/1045810/fixture-2026q2-8k.htm#p3

### wtw-2026q2-004

- from: Intel
- to: Public Sector Compute Reserve
- flow: wafer_start
- quantity: 9000 custom accelerator wafers
- confidence: 0.90-0.98
- status: disclosed
- evidence: https://www.sec.gov/Archives/edgar/data/1045810/fixture-2026q2-8k.htm#p4

## methodology

The parser strips cached HTML paragraphs and extracts commitment grammar matches. Every edge must carry a URL anchor and confidence interval.

## inferences and limits

Inferred edges: 1 of 4. The v0.1 gate fails if inferred edges exceed 30 percent of a quarter.
