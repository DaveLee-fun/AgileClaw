"""
KPI report prompt builders.
"""
from datetime import datetime


def build_daily_report_prompt(goals_content: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""Generate today's KPI progress report for {now}.

Goals and KPI definitions:
---
{goals_content}
---

Requirements:
1. Measure today's KPI values using tools.
2. Compare with targets.
3. Identify today's top risk KPI.
4. Suggest one immediate action for today.
5. Keep output concise and numeric.
"""


def build_weekly_report_prompt(goals_content: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""Generate this week's KPI review report for {now}.

Goals and KPI definitions:
---
{goals_content}
---

Requirements:
1. Measure current KPI values using tools.
2. Summarize weekly progress vs target.
3. List what worked and what failed.
4. Provide top 3 actions for next week.
5. Include a compact KPI table.
"""
