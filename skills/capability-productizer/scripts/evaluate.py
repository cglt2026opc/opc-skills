#!/usr/bin/env python3
"""Evaluate candidate capabilities from a JSON list."""
import json
import sys
from pathlib import Path

def classify(item):
    required = ["depth", "demand", "advantage"]
    unknown = [key for key in required + ["ai_leverage"] if key not in item or item[key] is None]
    if unknown:
        return "待验证", unknown
    if not item["demand"]:
        return "先验证需求", []
    if not item["depth"] or not item["advantage"]:
        return "先沉淀交付", []
    if str(item["ai_leverage"]).lower() != "high":
        return "可服务化，产品化提效不足", []
    return "可优先产品化", []

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: evaluate.py INPUT.json")
    items = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise SystemExit("input must be a JSON list")
    output = []
    for item in items:
        status, unknown = classify(item)
        output.append({"name": item.get("name", "未命名能力"), "status": status, "unknown": unknown})
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

