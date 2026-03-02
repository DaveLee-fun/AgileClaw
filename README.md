# AgileClaw 🦾

A lightweight autonomous agent for KPI-driven execution.

Core philosophy:
- Keep the core small
- Move domain logic to skills
- Add new capabilities as tool plugins
- Every goal runs as an Agile Team with measurable KPIs

## Core Features

1. Telegram/CLI conversation
2. Claude tool-use agent loop
3. Tool plugins auto-discovery (`tools/*.py`)
4. Skill catalog (`skills/*/SKILL.md`)
5. Cron scheduler with action routing (`chat`, `agile_review`, `run_skill`)
6. Agile review loop from `memory/goals.md`
7. Goal-based Agile Team setup (`memory/teams/team-*.md`)
8. Generic KPI tools + optional platform KPI tools

## Quick Start

```bash
cp config.example.yaml config.yaml
# fill bot token + Claude API key

pip install -r requirements.txt
playwright install chromium
python main.py
```

## Configuration

`config.yaml` example:

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

## Telegram Commands

- `/start` — help
- `/goal <name> | <objective> [| <kpi_hint>]` — create Agile Team for a goal
- `/teams` — list Agile Teams
- `/agile` — run agile KPI review
- `/report [daily|weekly]` — generate KPI report
- `/skills` — list installed skills
- `/runskill <skill_key> [instruction]` — execute a skill
- `/cron` — list scheduled jobs

## Tool Plugin Interface

Any `tools/*.py` module can export `get_tool_specs()`:

```python
def get_tool_specs() -> list[dict]:
    return [
        {
            "definition": {
                "name": "my_tool",
                "description": "...",
                "input_schema": {...},
            },
            "handler": my_handler,  # (tool_input, context) -> str
        }
    ]
```

No central registration edit is needed.

## Skills

Create skills under:

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

## Cron Job Format

`cron_jobs.json` job entry:

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

Supported `action`:
- `chat`
- `agile_review`
- `daily_report`
- `weekly_report`
- `run_skill`

You can bootstrap from `cron_jobs.example.json`.

## Built-in KPI Tools

- `kpi_upsert_metric`: register/update KPI metrics for a team
- `kpi_log_measurement`: append KPI measurements
- `kpi_list_metrics`: view team KPI status
- `threads_get_followers`: Threads Graph API follower/metric fetch (optional)
- `reddit_get_karma`: Reddit public karma summary fetch (optional)

Agile loop itself is metric-agnostic. Platform-specific tools are optional.
Add any KPI source as another tool plugin under `tools/*.py`.

## Tests

```bash
cd src
python3 -m unittest discover -s tests -v
```

## Project Structure

```text
src/
├── main.py
├── cron_jobs.example.json
├── core/
│   ├── agent.py
│   ├── claude.py
│   ├── memory.py
│   └── skills.py
├── channels/
│   └── telegram.py
├── scheduler/
│   └── cron.py
├── tools/
│   ├── __init__.py
│   ├── shell.py
│   ├── files.py
│   ├── web.py
│   ├── browser.py
│   ├── kpi.py
│   ├── threads.py
│   └── reddit.py
├── agile/
│   ├── loop.py
│   ├── report.py
│   └── team.py
└── skills/
    ├── agile-weekly-review/SKILL.md
    └── kpi-daily-check/SKILL.md
```
