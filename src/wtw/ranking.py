"""Edge ranking shared by `wtw show` and the Streamlit view.

A snapshot mixes units (GB200 systems, MI300 accelerators, custom accelerator
wafers), and nothing in the data converts one into another. So rank is
disclosed-first, then confidence midpoint, and a raw quantity only orders edges
that share a unit. When the top edges tie and their units differ, there is no
single strongest edge: the tie is reported and every tied edge is listed.
"""
from __future__ import annotations

from typing import Any

Row = dict[str, Any]


def confidence_midpoint(row: Row) -> float:
    # Rounded so bands with the same real midpoint (0.80-0.90 and 0.75-0.95)
    # compare equal instead of differing by a float rounding step.
    return round((float(row["confidence_low"]) + float(row["confidence_high"])) / 2, 9)


def _rank(row: Row) -> tuple[bool, float]:
    # higher is stronger: disclosed (not inferred) first, then confidence
    return (not row.get("inferred", False), confidence_midpoint(row))


def _quantity(row: Row) -> float:
    return float(row.get("quantity", 0))


def rank_rows(rows: list[Row]) -> list[Row]:
    """Order rows strongest-first.

    Rows of equal rank are grouped by unit, and quantity orders them only inside
    a unit. Each sort is stable, so the last key applied is the primary one.
    """
    ordered = sorted(rows, key=_quantity, reverse=True)
    ordered = sorted(ordered, key=lambda r: str(r.get("quantity_unit", "")))
    return sorted(ordered, key=_rank, reverse=True)


def strongest_edges(rows: list[Row]) -> list[Row]:
    """Return the edge(s) holding the top rank.

    Quantity breaks a tie only between edges that share a unit, the one case
    where it is a unit-consistent measure: inside each unit only the largest
    quantity (or quantities, if equal) stays. Edges left in different units are
    all returned, in `rank_rows` order.
    """
    if not rows:
        return []
    top = max(_rank(r) for r in rows)
    tied = [r for r in rank_rows(rows) if _rank(r) == top]
    most: dict[Any, float] = {}
    for r in tied:
        unit = r.get("quantity_unit")
        most[unit] = max(most.get(unit, _quantity(r)), _quantity(r))
    return [r for r in tied if _quantity(r) == most[r.get("quantity_unit")]]


def _status(row: Row) -> str:
    return "inferred" if row.get("inferred") else "disclosed"


def _band(row: Row) -> str:
    return f"{float(row['confidence_low']):.2f}-{float(row['confidence_high']):.2f}"


def describe_edge(row: Row) -> str:
    return (
        f"{row.get('from_entity')} -> {row.get('to_entity')} — "
        f"{_quantity(row):,.0f} {row.get('quantity_unit')} "
        f"({_status(row)}, confidence {_band(row)}). "
        f"evidence: {row.get('evidence_url')}"
    )


def describe_tie(tied: list[Row]) -> str:
    """One clause saying why the tied edges from `strongest_edges` stay tied."""
    bands = {_band(r) for r in tied}
    confidence = (
        f"confidence {bands.pop()}"
        if len(bands) == 1
        else f"confidence midpoint {confidence_midpoint(tied[0]):.2f}"
    )
    units = {r.get("quantity_unit") for r in tied}
    why = (
        "their quantities are in different units, so none outranks the others"
        if len(units) > 1
        else "they also have the same quantity in the same unit"
    )
    return f"{len(tied)} {_status(tied[0])} edges share the top {confidence}; {why}"
