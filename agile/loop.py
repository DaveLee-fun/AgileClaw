"""
Agile loop — the core of AgileClaw.
Reads goals.md → measures current state → compares vs targets → suggests improvements.
"""
from datetime import datetime


AGILE_SYSTEM_PROMPT = """You are an agile team AI. Your job is to:
1. Read the current goals and KPIs from goals.md
2. Measure the current state using available tools
3. Compare actual vs target
4. Identify what's working and what's not
5. Suggest concrete next actions to improve

Be data-driven. Be specific. Keep suggestions actionable.
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

## Sprint: [Sprint Name]
Period: [Start] → [End]

## KPIs

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| [Metric 1] | [value] | [target] | 🟡 |
| [Metric 2] | [value] | [target] | 🔴 |

## This Week's Focus
1. [Top priority]
2. [Second priority]
3. [Third priority]

## How to Measure
- [Metric 1]: [How to check — e.g., run script X, check API Y]
- [Metric 2]: [How to check]

## Notes
[Any context for the AI to understand the goals]
"""
