import pytest

from src.wtw.validation import check_rows

CHECK = "confidence interval well-formed in [0, 1]"


def _gate(low, high):
    result = check_rows([{"edge_id": "synthetic", "inferred": False, "evidence_url": "https://example.test", "confidence_low": low, "confidence_high": high}])
    return next(r for r in result if r["check"] == CHECK)


@pytest.mark.parametrize("low,high", [(-0.1, 0.8), (0.1, 1.1), (float("nan"), 0.8), (0.2, float("inf")), (False, True), (0.1, 10 ** 400), ("0.5", "0.9"), (0.5, " 1 "), (None, 0.9)])
def test_confidence_gate_rejects_unbounded_nonfinite_or_non_numeric_intervals(low, high):
    assert _gate(low, high)["passed"] is False


@pytest.mark.parametrize("low,high", [(0, 0), (0, 1), (1, 1), (0.0, 1.0), (0.9, 0.98)])
def test_confidence_gate_accepts_schema_inclusive_bounds(low, high):
    assert _gate(low, high)["passed"] is True
