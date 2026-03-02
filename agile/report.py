"""
KPI report prompt builders.
"""
from datetime import datetime


def _team_refs_section(team_refs: str) -> str:
    refs = (team_refs or "").strip()
    if not refs:
        return "Goal team charters:\n- (none)"
    return f"Goal team charters:\n---\n{refs}\n---"


def build_daily_report_prompt(goals_content: str, team_refs: str = "") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    teams_block = _team_refs_section(team_refs)
    return f"""Generate today's KPI progress report for {now}.

Goals and KPI definitions:
---
{goals_content}
---

{teams_block}

Requirements:
1. Measure today's KPI values using tools.
2. Compare with targets.
3. Identify today's top risk KPI.
4. Suggest one immediate action for today.
5. Keep output concise and numeric.
"""


def build_weekly_report_prompt(goals_content: str, team_refs: str = "") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    teams_block = _team_refs_section(team_refs)
    return f"""Generate this week's KPI review report for {now}.

Goals and KPI definitions:
---
{goals_content}
---

{teams_block}

Requirements:
1. Measure current KPI values using tools.
2. Summarize weekly progress vs target.
3. List what worked and what failed.
4. Provide top 3 actions for next week.
5. Include a compact KPI table.
"""
