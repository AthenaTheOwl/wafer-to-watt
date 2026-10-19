from src.wtw.ranking import describe_tie, rank_rows, strongest_edges


def _edge(edge_id: str, quantity: float, unit: str, **overrides: object) -> dict[str, object]:
    row = {
        "edge_id": edge_id,
        "from_entity": f"from-{edge_id}",
        "to_entity": f"to-{edge_id}",
        "quantity": quantity,
        "quantity_unit": unit,
        "inferred": False,
        "confidence_low": 0.90,
        "confidence_high": 0.98,
        "evidence_url": f"https://example.invalid/{edge_id}",
    }
    row.update(overrides)
    return row


def _ids(rows: list[dict[str, object]]) -> list[object]:
    return [r["edge_id"] for r in rows]


def test_tie_across_units_lists_every_tied_edge_instead_of_the_biggest_number() -> None:
    systems = _edge("systems", 50_000, "GB200 systems")
    wafers = _edge("wafers", 9_000, "custom accelerator wafers")
    inferred = _edge("inferred", 120_000, "custom accelerator wafers", inferred=True,
                     confidence_low=0.70, confidence_high=0.88)
    top = strongest_edges([wafers, inferred, systems])
    assert sorted(_ids(top)) == ["systems", "wafers"]
    assert "different units" in describe_tie(top)


def test_quantity_breaks_a_tie_only_within_one_unit() -> None:
    small = _edge("small", 9_000, "custom accelerator wafers")
    large = _edge("large", 12_000, "custom accelerator wafers")
    assert _ids(strongest_edges([small, large])) == ["large"]


def test_equal_quantity_in_one_unit_stays_tied() -> None:
    a = _edge("a", 9_000, "custom accelerator wafers")
    b = _edge("b", 9_000, "custom accelerator wafers")
    top = strongest_edges([a, b])
    assert sorted(_ids(top)) == ["a", "b"]
    assert "same quantity in the same unit" in describe_tie(top)


def test_confidence_outranks_quantity_and_disclosed_outranks_inferred() -> None:
    sure = _edge("sure", 10, "GB200 systems", confidence_low=0.95, confidence_high=0.99)
    big = _edge("big", 50_000, "GB200 systems")
    inferred = _edge("inferred", 1_000_000, "GB200 systems", inferred=True,
                     confidence_low=0.99, confidence_high=1.0)
    assert _ids(strongest_edges([big, inferred, sure])) == ["sure"]
    assert _ids(rank_rows([inferred, big, sure])) == ["sure", "big", "inferred"]


def test_rank_rows_orders_quantity_only_inside_a_unit() -> None:
    rows = [
        _edge("w-small", 100, "custom accelerator wafers"),
        _edge("s", 5, "GB200 systems"),
        _edge("w-large", 200, "custom accelerator wafers"),
    ]
    ranked = _ids(rank_rows(rows))
    # the two wafer rows sit together, larger first; systems and wafers never
    # get compared by raw quantity
    assert ranked.index("w-large") + 1 == ranked.index("w-small")
    assert ranked == ["s", "w-large", "w-small"]


def test_empty_snapshot_has_no_strongest_edge() -> None:
    assert strongest_edges([]) == []
