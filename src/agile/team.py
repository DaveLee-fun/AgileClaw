"""
Agile Team helpers.

Each user request goal can become an independent Agile Team,
with its own charter, KPIs, and execution cadence.
"""
from datetime import datetime
import hashlib
import re
import unicodedata
import uuid


def slugify(text: str) -> str:
    value = (text or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "goal"


def _normalize_goal_text(goal_name: str) -> str:
    normalized = unicodedata.normalize("NFKC", (goal_name or "").strip().lower())
    return normalized or "goal"


def make_goal_key(goal_name: str) -> str:
    """
    Stable key for goal-team reuse.
    Uses normalized goal text hash to avoid collisions (e.g., non-ASCII goals).
    """
    normalized = _normalize_goal_text(goal_name)
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]
    return f"goal-{digest}"


def make_team_id(goal_name: str) -> str:
    normalized = _normalize_goal_text(goal_name)
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:8]
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    rand = uuid.uuid4().hex[:6]
    return f"team-{slugify(goal_name)}-{digest}-{ts}-{rand}"


def build_team_charter(team_id: str, goal_name: str, objective: str, kpi_hint: str = "") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    hint = kpi_hint.strip() or "Define 3-5 measurable KPIs for this goal."

    return f"""# Agile Team Charter

- Team ID: {team_id}
- Goal Name: {goal_name}
- Created At: {now}

## Objective
{objective}

## KPI Scope
{hint}

## KPIs

| Metric | Current | Target | Source | Frequency | Status |
|--------|---------|--------|--------|-----------|--------|
| [Metric 1] | [value] | [target] | [source] | daily | 🟡 |
| [Metric 2] | [value] | [target] | [source] | weekly | 🔴 |

## Backlog
1. [First high-impact action]
2. [Second action]
3. [Third action]

## Cadence
- Daily: KPI check + blockers
- Weekly: review + next sprint planning

## Notes
This team is one goal-specific Agile execution unit.
"""


def build_team_bootstrap_prompt(team_id: str, team_file_path: str, user_instruction: str = "") -> str:
    extra = user_instruction.strip() or "(No extra instruction provided.)"
    return f"""Initialize and run the first sprint plan for this Agile Team.

Team ID: {team_id}
Team charter file: {team_file_path}

Steps:
1. Read the team charter file.
2. Refine KPI definitions into measurable metrics.
3. Propose this week's top 3 execution actions.
4. If needed, update the team charter file with concrete KPI/source details.
5. Return concise sprint kickoff summary.

Extra instruction: {extra}
"""


def build_team_update_prompt(team_id: str, team_file_path: str, user_instruction: str = "") -> str:
    extra = user_instruction.strip() or "(No extra instruction provided.)"
    return f"""Continue execution for an existing Agile Team.

Team ID: {team_id}
Team charter file: {team_file_path}

Steps:
1. Read the team charter file.
2. Re-confirm KPI measurement definitions.
3. Measure latest KPI values and identify highest-risk metric.
4. Propose next sprint actions (top 3) and update backlog if needed.
5. Return concise progress + next steps.

Extra instruction: {extra}
"""
