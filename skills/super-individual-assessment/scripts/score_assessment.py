#!/usr/bin/env python3
"""Score the four-pillar assessment from a JSON file."""
import json
import sys
from pathlib import Path

DIMENSIONS = {
    "product_thinking": ["end_to_end", "demand_judgment"],
    "domain_depth": ["problem_insight", "paid_expertise"],
    "second_skill": ["valuable_second_skill", "skill_synergy"],
    "ai_leverage": ["speed_leverage", "stable_workflow"],
}
LABELS = {
    "product_thinking": "产品思维",
    "domain_depth": "主业深度",
    "second_skill": "第二技能",
    "ai_leverage": "AI 杠杆",
}

def tier(total):
    if total >= 70:
        return "超级个体预备役"
    if total >= 50:
        return "能力具备，需整合优势"
    if total >= 30:
        return "基础扎实，需补齐短板"
    return "仍在积累期，需系统学习"

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: score_assessment.py INPUT.json")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    scores = data.get("scores", data)
    evidence = data.get("evidence", {})
    required = [item for items in DIMENSIONS.values() for item in items]
    missing = [key for key in required if key not in scores]
    if missing:
        raise SystemExit("missing scores: " + ", ".join(missing))
    for key in required:
        value = scores[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 10:
            raise SystemExit(f"{key} must be a number from 0 to 10")
    subtotals = {key: sum(scores[item] for item in items) for key, items in DIMENSIONS.items()}
    total = sum(subtotals.values())
    low = min(subtotals.values())
    high = max(subtotals.values())
    result = {
        "total": total,
        "max_total": 80,
        "tier": tier(total),
        "dimensions": {LABELS[key]: value for key, value in subtotals.items()},
        "weakest": [LABELS[key] for key, value in subtotals.items() if value == low],
        "strongest": [LABELS[key] for key, value in subtotals.items() if value == high],
        "evidence_gaps": [key for key in required if not str(evidence.get(key, "")).strip()],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

