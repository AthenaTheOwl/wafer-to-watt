from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from .models import CommitmentEdge


class ParagraphParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_p = False
        self._current: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "p":
            self._in_p = True
            self._current = []

    def handle_data(self, data: str) -> None:
        if self._in_p:
            self._current.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "p" and self._in_p:
            text = " ".join(part.strip() for part in self._current if part.strip())
            if text:
                self.paragraphs.append(re.sub(r"\s+", " ", text))
            self._in_p = False


PATTERN = re.compile(
    r"(?P<from>[A-Z][A-Za-z0-9 .-]+) disclosed (?P<qty>[0-9,]+) "
    r"(?P<unit>GB200 systems|MI300 accelerators|custom accelerator wafers) "
    r"for (?P<to>[A-Z][A-Za-z0-9 .-]+?)(?= in this fixture paragraph|;|\\.)",
)


def paragraphs_from_html(path: Path) -> list[str]:
    parser = ParagraphParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.paragraphs


def parse_commitments(path: Path, quarter: str, evidence_url: str) -> list[CommitmentEdge]:
    edges: list[CommitmentEdge] = []
    for index, paragraph in enumerate(paragraphs_from_html(path), start=1):
        match = PATTERN.search(paragraph)
        if not match:
            continue
        quantity = float(match.group("qty").replace(",", ""))
        unit = match.group("unit")
        flow_kind = "accelerator_commit"
        if "wafers" in unit:
            flow_kind = "wafer_start"
        edge_id = f"wtw-{quarter}-{index:03d}"
        inferred = "inferred" in paragraph.lower()
        edges.append(
            CommitmentEdge(
                edge_id=edge_id,
                quarter=quarter,
                from_entity=match.group("from").strip(),
                to_entity=match.group("to").strip(),
                flow_kind=flow_kind,
                quantity=quantity,
                quantity_unit=unit,
                confidence_low=0.70 if inferred else 0.90,
                confidence_high=0.88 if inferred else 0.98,
                evidence_url=f"{evidence_url}#p{index}",
                evidence_timestamp=f"{quarter}-fixture-p{index}",
                inferred=inferred,
                extraction_mode="fixture",
            )
        )
    return edges
