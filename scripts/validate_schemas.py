from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[object]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main() -> int:
    try:
        import jsonschema
    except ImportError as exc:
        raise SystemExit("jsonschema is required") from exc
    schema_path = ROOT / "schemas" / "commitment.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema).check_schema(schema)
    for path in (ROOT / "data" / "snapshots").glob("*.jsonl"):
        for row in read_jsonl(path):
            jsonschema.validate(row, schema)
    print("validate_schemas OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

