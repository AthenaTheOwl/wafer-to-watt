from pathlib import Path

import pytest

from src.wtw.report import ILLUSTRATIVE_NOTE

# streamlit is an app dependency (requirements.txt), not a project one, so CI's
# `uv run --with pytest` skips these; run them where streamlit is installed.
AppTest = pytest.importorskip("streamlit.testing.v1").AppTest

APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def _run() -> "AppTest":
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not at.exception
    return at


def test_app_labels_fixture_snapshot_illustrative() -> None:
    at = _run()
    assert at.subheader[0].value.endswith("(illustrative)")
    assert ILLUSTRATIVE_NOTE in [w.value for w in at.warning]


def test_app_states_the_strongest_edge_tie_instead_of_picking_by_quantity() -> None:
    callout = _run().info[0].value
    assert callout.startswith("**strongest edge: tie**")
    assert [line[2:10] for line in callout.splitlines() if line.startswith("- ")] == [
        "Vendor A",
        "Vendor B",
        "Vendor D",
    ]
