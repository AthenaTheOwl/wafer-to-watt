# WaferToWatt allocations - 2026q2 (illustrative fixture)

**Illustrative fixture data.** The vendors, buyers, quantities and evidence anchors
below are synthetic, not real disclosures.

Fixture-backed accelerator commitment edges parsed from synthetic filing-style text.
The report is a pipeline proof, not a live allocation claim.

## edges

### wtw-2026q2-001

- from: Vendor A
- to: CloudCo AI Factory
- flow: accelerator_commit
- quantity: 50000 GB200 systems
- confidence: 0.90-0.98
- status: disclosed
- evidence: https://example.invalid/fixtures/edgar/2026q2_8k_fixture.html#p1

### wtw-2026q2-002

- from: Vendor B
- to: ResearchGrid Compute
- flow: accelerator_commit
- quantity: 18000 MI300 accelerators
- confidence: 0.90-0.98
- status: disclosed
- evidence: https://example.invalid/fixtures/edgar/2026q2_8k_fixture.html#p2

### wtw-2026q2-003

- from: Vendor C
- to: Atlas Hyperscale
- flow: wafer_start
- quantity: 120000 custom accelerator wafers
- confidence: 0.70-0.88
- status: inferred
- evidence: https://example.invalid/fixtures/edgar/2026q2_8k_fixture.html#p3

### wtw-2026q2-004

- from: Vendor D
- to: Public Sector Compute Reserve
- flow: wafer_start
- quantity: 9000 custom accelerator wafers
- confidence: 0.90-0.98
- status: disclosed
- evidence: https://example.invalid/fixtures/edgar/2026q2_8k_fixture.html#p4

## methodology

The parser strips cached HTML paragraphs and extracts commitment grammar matches. Every edge must carry a URL anchor and confidence interval.

## inferences and limits

Inferred edges: 1 of 4. The v0.1 gate fails if inferred edges exceed 30 percent of a quarter.
