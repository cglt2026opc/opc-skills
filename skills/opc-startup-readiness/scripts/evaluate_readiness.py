#!/usr/bin/env python3
"""Evaluate the 12-item OPC readiness checklist."""
import json
import sys
from pathlib import Path

KEYS = [
    "stable_demand", "repeatable_delivery", "clear_employment_boundary",
    "no_noncompete_breach", "no_employer_resources", "no_job_performance_harm",
    "startup_budget", "six_month_runway", "subsidy_research",
    "clear_positioning", "stable_acquisition", "reusable_delivery",
]
HARD_STOPS = {"clear_employment_boundary", "no_noncompete_breach", "no_employer_resources", "no_job_performance_harm"}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: evaluate_readiness.py INPUT.json")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    missing = [key for key in KEYS if key not in data]
    if missing:
        raise SystemExit("missing items: " + ", ".join(missing))
    invalid = [key for key in KEYS if data[key] not in (True, False, None)]
    if invalid:
        raise SystemExit("values must be true, false, or null: " + ", ".join(invalid))
    completed = sum(data[key] is True for key in KEYS)
    blockers = [key for key in HARD_STOPS if data[key] is not True]
    gaps = [key for key in KEYS if data[key] is not True]
    if blockers:
        status = "暂缓：先解决主副业边界或合规风险"
    elif completed == 12:
        status = "可以开始低成本验证"
    elif completed >= 9:
        status = "可小范围试运行（操作性建议，非书中评分）"
    else:
        status = "准备不足，先补关键缺口"
    print(json.dumps({"completed": completed, "total": 12, "status": status, "hard_stop_gaps": blockers, "all_gaps": gaps}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

