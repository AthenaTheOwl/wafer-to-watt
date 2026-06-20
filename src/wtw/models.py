from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CommitmentEdge:
    edge_id: str
    quarter: str
    from_entity: str
    to_entity: str
    flow_kind: str
    quantity: float
    quantity_unit: str
    confidence_low: float
    confidence_high: float
    evidence_url: str
    evidence_timestamp: str
    inferred: bool
    extraction_mode: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

