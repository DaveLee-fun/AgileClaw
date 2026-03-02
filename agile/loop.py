"""
Agile loop — the core of AgileClaw.
Reads goals.md → measures current state → compares vs targets → suggests improvements.
"""
from datetime import datetime


AGILE_SYSTEM_PROMPT = """You are an agile team AI. Your job is to:
1. Treat each request goal as an independent Agile Team execution unit.
2. Read the current goals and KPIs from goals.md and/or team charter files.
3. Confirm how each KPI is measured (source, frequency, numeric definition) before execution.
4. Measure current state using available tools.
5. Compare actual vs target and identify what's working and not working.
6. Suggest concrete next actions to improve.

Be data-driven. Be specific. Keep suggestions actionable.
Use generic KPI tools first (kpi_upsert_metric, kpi_log_measurement, kpi_list_metrics).
Use KPI-specific tools when available (e.g., threads_get_followers, reddit_get_karma).
Format your response as:
- 📊 Current State (with actual numbers)
- 🎯 vs Target (gap analysis)  
- ✅ What's working
- ⚠️ What's not working
- 🚀 Next actions (top 3, concrete steps)
"""


def build_agile_prompt(goals_content: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""Run the agile review for {today}.

Current goals and KPIs:
---
{goals_content}
---

Use your tools to measure the current state, compare vs targets, and suggest improvements.
"""


GOALS_TEMPLATE = """# AgileClaw Goals

## Sprint: Multi-Goal Agile Sprint
Period: 2026-03-02 → 2026-03-08

## Goal Teams
- team-growth-threads: Social growth objective
- team-revenue-product: Revenue optimization objective

## Global KPI Snapshot

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Threads followers (optional) | 160 | 250 | 🟡 |
| Reddit total karma (optional) | 1200 | 1500 | 🟡 |
| App downloads | 42 | 80 | 🔴 |
| Daily revenue (USD) | 120 | 300 | 🔴 |

## This Week's Focus
1. For every goal request, create or update a dedicated Agile Team charter.
2. Confirm KPI measurement method first, then execute.
3. Prioritize the highest-risk KPI in each team.

## How to Measure
- Use generic KPI tools for team metrics (kpi_upsert_metric, kpi_log_measurement, kpi_list_metrics)
- Use KPI-specific tool if available (e.g., threads_get_followers, reddit_get_karma)
- If dashboard metric, fetch from analytics URL or input source
- If no data source yet, define temporary proxy metric with confidence note

## Notes
Agile loop is metric-agnostic. Platform-specific tools are optional.
"""
