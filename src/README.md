# AgileClaw

AgileClaw is a lightweight autonomous agent for KPI-driven execution.
Current version: `0.1.0`

Core principles:
- Keep the core small.
- Treat each goal request as an Agile Team unit.
- Confirm KPI measurement method first, then execute.
- Extend capability through tool plugins and skills.

## What Works Now

1. Telegram and CLI conversation interfaces.
2. Claude tool-use loop (`core/claude.py`).
3. Auto goal-team setup from chat goal requests.
4. Explicit goal-team commands (`/goal`, `/teams`, CLI `goal`, `teams`).
5. Agile review and KPI reports (`/agile`, `/report daily|weekly`).
6. Tool plugin auto-discovery from `tools/*.py`.
7. Skill catalog from `skills/*/SKILL.md`.
8. Cron scheduler with action routing and schedule validation.
9. Generic KPI data layer plus optional platform KPI tools.

## Quick Start

```bash
cp config.example.yaml config.yaml
# fill Telegram bot token and Claude API key

pip install -r requirements.txt
playwright install chromium
python main.py
```

## Configuration

Example `config.yaml`:

```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  allowed_users: [123456789]

claude:
  api_key: "YOUR_CLAUDE_API_KEY"
  model: "claude-sonnet-4-5"
  max_tokens: 4096
  max_tool_rounds: 10
  max_retries: 2
  retry_base_delay: 1.0

memory:
  dir: "./memory"

skills:
  dir: "./skills"

cron:
  jobs_file: "./cron_jobs.json"

browser:
  headless: false
```

If `telegram` is omitted, app starts in interactive CLI mode.

## Goal-Team Workflow

1. User sends a goal-like request.
2. Agent auto-creates or reuses a team charter in `memory/teams/`.
3. Agent asks/defines measurement method (source, frequency, numeric target).
4. Agent executes and iterates by Agile loop.

Notes:
- `run_skill` does not trigger auto goal-team setup (skill prompt is treated as operational instruction).
- Team index supports legacy key migration and collision-safe hashing for non-ASCII goals.

## Telegram Commands

- `/start` help
- `/goal <name> | <objective> [| <kpi_hint>]`
- `/teams`
- `/agile`
- `/report [daily|weekly]`
- `/skills`
- `/runskill <skill_key> [instruction]`
- `/cron`

## CLI Commands

- `agile`
- `skills`
- `teams`
- `goal <name> | <objective> [| <kpi_hint>]`
- `skill <skill_key> [instruction]`
- `quit`

## Cron Jobs

Job format (`cron_jobs.json`):

```json
{
  "id": "abcd1234",
  "name": "daily-kpi",
  "schedule": "0 9 * * *",
  "action": "run_skill",
  "skill": "kpi-daily-check",
  "message": "오늘 KPI 체크하고 리스크 정리해줘",
  "chat_id": "123456",
  "enabled": true
}
```

Supported actions:
- `chat`
- `agile_review`
- `daily_report`
- `weekly_report`
- `run_skill`

Schedule formats:
- Cron: `"0 9 * * *"`
- Interval: `"every 30m"`, `"every 1h"`, `"every 2d"`, `"every 45s"`

Runtime behavior:
- Invalid schedule is rejected at add time.
- Corrupted/invalid jobs file is ignored safely.
- Invalid persisted jobs are skipped, not fatal.

## Tool Plugins

Any module in `tools/*.py` can expose:

```python
def get_tool_specs() -> list[dict]:
    return [
        {
            "definition": {
                "name": "my_tool",
                "description": "...",
                "input_schema": {...}
            },
            "handler": my_handler  # (tool_input: dict, context: dict) -> str
        }
    ]
```

Notes:
- No central tool registry edit required.
- Duplicate tool names are rejected and logged.

## Built-in KPI Tools

- `kpi_upsert_metric`
- `kpi_log_measurement`
- `kpi_list_metrics`
- `threads_get_followers` (optional)
- `reddit_get_karma` (optional)

Agile loop is metric-agnostic. Add more KPI sources as tool plugins.

## Skills

Create skill folders:

```text
skills/<skill_name>/SKILL.md
```

Recommended frontmatter:

```md
---
name: my-skill
description: What this skill does
---
```

## Memory Files

`memory/` contains:
- `goals.md`
- `CONTEXT.md`
- `teams/index.json`
- `teams/team-*.md`
- `history-<chat_id>.json`
- `log-YYYY-MM-DD.md`
- `kpi_metrics.json`

## Tests

```bash
cd src
python3 -m unittest discover -s tests -v
python3 -m compileall -q .
```
