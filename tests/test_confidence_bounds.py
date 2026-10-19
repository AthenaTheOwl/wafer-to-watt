import pytest

from src.wtw.validation import check_rows


@pytest.mark.parametrize("low,high", [(-0.1, 0.8), (0.1, 1.1), (float("nan"), 0.8), (0.2, float("inf")), (False, True), (0.1, 10 ** 400)])
def test_confidence_gate_rejects_unbounded_or_nonfinite_intervals(low, high):
    result = check_rows([{"edge_id": "synthetic", "inferred": False, "evidence_url": "https://example.test", "confidence_low": low, "confidence_high": high}])
    assert next(r for r in result if r["check"] == "confidence interval not inverted")["passed"] is False
