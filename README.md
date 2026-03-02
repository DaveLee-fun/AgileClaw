<div align="center">

# 🦅 AgileClaw

### *A lightweight autonomous agent for KPI-driven execution*

> 🚧 **Early Stage — Not Yet Functional**
>
> This project is in its **initial development phase**. The code is being actively built and is **not ready to run yet**.
> APIs, config format, and structure will change significantly.
> Watch/Star to follow progress — contributions and ideas welcome!

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-orange.svg)](https://anthropic.com)
[![Telegram](https://img.shields.io/badge/channel-Telegram-blue.svg)](https://telegram.org)
[![Status](https://img.shields.io/badge/status-WIP-red.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

*Built for solo entrepreneurs, indie hackers, and small teams.*

[Quick Start](#-quick-start) · [How It Works](#telegram-commands) · [Architecture](#project-structure) · [Why AgileClaw](#why-agileclaw)

</div>

---

## Core Philosophy

- Keep the core small
- Move domain logic to skills
- Add new capabilities as tool plugins
- Every goal runs as an independent **Agile Team** with measurable KPIs

---

## Why AgileClaw?

Inspired by **[OpenClaw](https://github.com/openclaw/openclaw)** and **[nanoclaw](https://github.com/qwibitai/nanoclaw)** — same philosophy of giving AI full PC access, with the missing piece: a structured agile feedback loop so the agent actually improves your results over time.

| Feature | AgileClaw | OpenClaw | nanoclaw | AutoGen | LangChain |
|---------|:---------:|:--------:|:--------:|:-------:|:---------:|
| Built-in agile loop | ✅ | ❌ | ❌ | ❌ | ❌ |
| Auto Agile Team per goal | ✅ | ❌ | ❌ | ❌ | ❌ |
| Daily / weekly KPI reports | ✅ | ❌ | ❌ | ❌ | ❌ |
| Full PC access (no sandbox) | ✅ | ✅ | ✅ | ✅ | ❌ |
| Tool plugin auto-discovery | ✅ | ❌ | ❌ | ❌ | ❌ |
| Skill catalog (hot-reload) | ✅ | ✅ | ❌ | ❌ | ❌ |
| < 600 lines of core code | ✅ | ❌ | ✅ | ❌ | ❌ |
| Telegram native | ✅ | ✅ | ❌ | ❌ | ❌ |
| Cron scheduler built-in | ✅ | ✅ | ❌ | ❌ | ❌ |
| File-based memory (no DB) | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## Core Features

1. Telegram/CLI conversation
2. Claude tool-use agent loop
3. Tool plugins auto-discovery (`tools/*.py`)
4. Skill catalog (`skills/*/SKILL.md`)
5. Cron scheduler with action routing (`chat`, `agile_review`, `run_skill`, `daily_report`, `weekly_report`)
6. Agile review loop from `memory/goals.md`
7. Goal-based Agile Team setup (`memory/teams/team-*.md`)
8. Generic KPI tools + optional platform KPI tools

---

## ⚡ Quick Start

```bash
cp config.example.yaml config.yaml
# fill bot token + Claude API key

pip install -r requirements.txt
playwright install chromium
python main.py
```

---

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

---

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Show help |
| `/goal <name> \| <objective> [\| <kpi_hint>]` | Create Agile Team for a goal |
| `/teams` | List all active Agile Teams |
| `/agile` | Run agile KPI review |
| `/report [daily\|weekly]` | Generate KPI report |
| `/skills` | List installed skills |
| `/runskill <skill_key> [instruction]` | Execute a skill |
| `/cron` | List scheduled jobs |
| Just chat | Free conversation with the agent |

---

## Tool Plugin Interface

Any `tools/*.py` module can export `get_tool_specs()` — **no central registration needed**:

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

Drop a file in `tools/` and it's auto-discovered on startup (and hot-reloaded on each request).

---

## Skills

Create skills under `skills/<skill_name>/SKILL.md`:

```md
---
name: my-skill
description: What this skill does
---

## Steps
1. Run `python scripts/check_mrr.py`
2. Compare result vs goals.md target
3. Suggest top 3 actions if gap > 20%
```

Built-in skills:
- `kpi-daily-check` — Morning KPI snapshot
- `agile-weekly-review` — Friday retrospective

---

## Cron Job Format

`cron_jobs.json` example:

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

Supported `action` values: `chat` · `agile_review` · `daily_report` · `weekly_report` · `run_skill`

---

## Built-in KPI Tools

| Tool | Description |
|------|-------------|
| `kpi_upsert_metric` | Register / update a KPI metric definition |
| `kpi_log_measurement` | Append a measurement to a KPI metric |
| `kpi_list_metrics` | View all team KPI metrics and status |
| `threads_get_followers` | Threads Graph API follower/metric fetch *(optional)* |
| `reddit_get_karma` | Reddit public karma summary fetch *(optional)* |

The agile loop is metric-agnostic. Platform-specific tools are optional.
Add any KPI source as another tool plugin under `tools/*.py`.

---

## Tests

```bash
python3 -m unittest discover -s tests -v
```

---

## Project Structure

```
agileclaw/
├── main.py
├── config.example.yaml
├── cron_jobs.example.json
├── core/
│   ├── agent.py        # Agent brain: chat, agile review, team management
│   ├── claude.py       # Claude API client (tool_use loop, retry, rate limit)
│   ├── memory.py       # File-based memory + Agile Team registry
│   └── skills.py       # Skill catalog (hot-reload)
├── channels/
│   └── telegram.py     # Telegram bot (commands + free chat)
├── scheduler/
│   └── cron.py         # Cron job scheduler (APScheduler)
├── tools/
│   ├── __init__.py     # Auto-discovery: loads all tools/*.py
│   ├── shell.py
│   ├── files.py
│   ├── web.py
│   ├── browser.py      # Playwright browser control
│   ├── kpi.py          # KPI upsert / log / list
│   ├── threads.py      # Threads API
│   └── reddit.py       # Reddit API
├── agile/
│   ├── loop.py         # Agile system prompts + review builder
│   ├── report.py       # Daily/weekly report prompt builders
│   └── team.py         # Team charter creation, slugify, goal key
├── skills/
│   ├── kpi-daily-check/SKILL.md
│   └── agile-weekly-review/SKILL.md
└── tests/
```

---

## 🗺 Roadmap

- [x] Core Claude agent loop with tool_use
- [x] Telegram channel (commands + free chat)
- [x] Cron scheduler with action routing
- [x] Agile review loop
- [x] Auto Agile Team creation per goal
- [x] Daily / weekly report builders
- [x] File-based memory + team registry
- [x] Skill plugin system (hot-reload)
- [x] KPI tool (upsert, log, list)
- [x] Threads & Reddit API tools
- [x] Auto tool discovery (no registration)
- [ ] Discord channel support
- [ ] Web dashboard for KPI visualization
- [ ] Pre-built skill packs (App Store, Stripe, GitHub)
- [ ] Multi-agent delegation (spawn sub-agents per team)
- [ ] OpenClaw integration mode

---

## 🤝 Contributing

AgileClaw is intentionally small. Before adding features, ask:
> *"Can this be a custom tool or skill instead?"*

Great first contributions:
- New tool: `tools/slack.py`, `tools/notion.py`, `tools/stripe.py`
- New channel: `channels/discord.py`
- Example skill in `skills/`
- Bug fixes & tests

---

## 📜 License

MIT — do whatever you want with it.

---

<div align="center">

*Built on the shoulders of [OpenClaw](https://github.com/openclaw/openclaw) and [nanoclaw](https://github.com/qwibitai/nanoclaw).*
*If you find this useful, consider starring ⭐*

</div>
