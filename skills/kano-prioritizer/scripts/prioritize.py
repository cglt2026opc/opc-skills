#!/usr/bin/env python3
"""Sort KANO-classified requirements deterministically."""
import json
import sys
from pathlib import Path

ORDER = {"basic": 0, "performance": 1, "delighter": 2, "indifferent": 3, "reverse": 4}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: prioritize.py INPUT.json")
    items = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise SystemExit("input must be a JSON list")
    for item in items:
        kind = item.get("type")
        if kind not in ORDER:
            raise SystemExit(f"unknown type for {item.get('name', 'item')}: {kind}")
        for key in ("impact", "evidence", "effort"):
            value = item.get(key, 0)
            if not isinstance(value, (int, float)) or not 0 <= value <= 5:
                raise SystemExit(f"{key} must be 0..5")
    ranked = sorted(items, key=lambda x: (ORDER[x["type"]], -x.get("evidence", 0), -x.get("impact", 0), x.get("effort", 0), x.get("name", "")))
    print(json.dumps(ranked, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

