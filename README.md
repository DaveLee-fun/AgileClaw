<div align="center">

# 🦅 AgileClaw

### *The AI agent that measures → learns → improves on its own*

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-orange.svg)](https://anthropic.com)
[![Telegram](https://img.shields.io/badge/channel-Telegram-blue.svg)](https://telegram.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**A lightweight personal AI agent with a built-in agile loop.**  
Full PC access · Claude-powered · Telegram native · Cron scheduler  
*Built for solo entrepreneurs, indie hackers, and small teams.*

[Quick Start](#-quick-start-5-minutes) · [How It Works](#-how-the-agile-loop-works) · [Architecture](#-architecture) · [Use Cases](#-use-cases)

</div>

---

## What is AgileClaw?

AgileClaw is a **personal AI agent** that lives on your machine and runs a continuous agile loop:

> **Set goals → Measure KPIs → Analyze results → Improve automatically → Repeat**

It's not just another chatbot. AgileClaw **knows your goals**, **checks your metrics**, and **suggests concrete next steps** — every day, automatically.

Inspired by OpenClaw/nanoclaw's philosophy of giving AI full PC access, AgileClaw adds the missing piece: **a structured feedback loop so the agent actually gets better over time.**

**Who it's for:**
- 🧑‍💻 **Solo entrepreneurs** who want an AI that tracks their business KPIs
- 🚀 **Indie hackers** running multiple projects without a team
- 👥 **Small teams** who want agile rituals without the overhead

---

## Why AgileClaw?

| Feature | AgileClaw | AutoGen | CrewAI | LangChain |
|---------|:---------:|:-------:|:------:|:---------:|
| Built-in agile loop | ✅ | ❌ | ❌ | ❌ |
| Full PC access (no sandbox) | ✅ | ✅ | ❌ | ❌ |
| < 500 lines of core code | ✅ | ❌ | ❌ | ❌ |
| KPI-driven goals | ✅ | ❌ | ❌ | ❌ |
| Telegram native | ✅ | ❌ | ❌ | ❌ |
| Cron scheduler built-in | ✅ | ❌ | ❌ | ❌ |
| File-based memory (no DB) | ✅ | ❌ | ❌ | ❌ |
| Single config file | ✅ | ❌ | ❌ | ❌ |

---

## ⚡ Quick Start (5 minutes)

### 1. Clone & Install

```bash
git clone https://github.com/DaveLee-fun/AgileClaw.git
cd AgileClaw
./setup.sh
```

### 2. Configure

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys
```

```yaml
# config.yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN"       # Get from @BotFather
  allowed_users: [YOUR_USER_ID]     # Your Telegram user ID

claude:
  api_key: "YOUR_CLAUDE_API_KEY"    # From console.anthropic.com
  model: "claude-sonnet-4-5"

memory:
  dir: "./memory"
```

### 3. Set Your Goals

Edit `memory/goals.md`:

```markdown
# My Goals — March 2025

## KPIs
| Metric          | Current | Target  |
|-----------------|---------|---------|
| MRR             | $500    | $2,000  |
| Newsletter subs | 320     | 1,000   |
| App downloads   | 50/day  | 200/day |
```

### 4. Run

```bash
source venv/bin/activate
python main.py
```

Open Telegram, send a message, or type `/agile` to trigger a full review!

---

## 🔄 How the Agile Loop Works

```
┌─────────────────────────────────────────────────────────────┐
│                    THE AGILE LOOP                           │
│                                                             │
│   📋 GOALS          📊 MEASURE          🔍 ANALYZE          │
│   goals.md    ──►   shell/web     ──►   actual vs target   │
│   KPI targets       API calls          gap analysis         │
│       │             file checks            │                │
│       │                                    ▼                │
│       │          🔄 REPEAT           🚀 IMPROVE             │
│       └──────────────────────◄──── concrete next steps     │
│                (daily/weekly)      top 3 actions            │
│                                    saved to memory          │
└─────────────────────────────────────────────────────────────┘
```

**Trigger the loop:**
- **Manually:** `/agile` in Telegram
- **Automatically:** Configure a cron job (e.g., every morning at 9 AM)
- **On demand:** Ask the agent naturally: *"How are my goals looking this week?"*

**What the agent does:**
1. Reads your `goals.md` with current KPIs and targets
2. Uses tools (shell, browser, web fetch) to **measure actual values**
3. Compares actual vs target — identifies gaps
4. Returns a structured report with **top 3 actionable next steps**

---

## 🏗 Architecture

```
AgileClaw/
├── main.py                 # Entry point — boots agent + channels
│
├── core/
│   ├── agent.py            # Brain — routes messages, calls Claude, uses tools
│   ├── claude.py           # Claude API wrapper with tool_use loop
│   └── memory.py           # File-based memory — history, goals, context, logs
│
├── channels/
│   └── telegram.py         # Telegram bot — /start, /agile, /cron, messages
│
├── tools/
│   ├── shell.py            # Execute any shell command on host machine
│   ├── files.py            # Read/write files
│   ├── web.py              # Fetch URLs and web pages
│   └── browser.py          # Playwright browser control (click, type, screenshot)
│
├── scheduler/
│   └── cron.py             # APScheduler — interval & cron string support
│
├── agile/
│   ├── loop.py             # Agile loop logic — prompts and goal parsing
│   └── goals.md            # Your goals and KPIs (edit this!)
│
├── memory/                 # Auto-created — conversation history, logs
├── config.yaml             # Your config (gitignored)
└── config.example.yaml     # Template
```

**Key design decisions:**
- **No database** — everything is plain files (goals.md, history-*.json, logs)
- **No framework** — raw Claude API with a clean tool_use loop (~100 lines)
- **No Docker** — runs directly on your machine with full access
- **Composable** — add new tools by adding one Python file

---

## 🛠 Tools Available

The agent can use these tools out of the box:

| Tool | What it does | Example use |
|------|-------------|-------------|
| `shell` | Run any bash command | Check git commits, run scripts, ping APIs |
| `read_file` | Read any file | Load reports, configs, logs |
| `write_file` | Write files | Update dashboards, save reports |
| `web_fetch` | Fetch any URL | Check website analytics, scrape prices |
| `browser_open` | Open URL in browser | Navigate to dashboards |
| `browser_click` | Click page elements | Automate web workflows |
| `browser_type` | Type into inputs | Fill forms automatically |
| `browser_get_text` | Extract page text | Read dynamic content |
| `browser_screenshot` | Capture screenshots | Document current state |

---

## 💡 Use Cases

### 1. 📈 Daily Business Review
> *"How are my metrics looking today?"*

The agent checks your Stripe MRR, newsletter subscriber count (via Mailchimp API), and app store downloads — then tells you the gap vs your monthly target and what to do next.

### 2. 📝 Content Pipeline Manager
> *"I need 3 blog post ideas based on trending topics in my niche"*

The agent fetches Reddit/HN trending posts, analyzes what gets traction, and generates ideas tailored to your audience — saved directly to your content calendar file.

### 3. 🔔 Smart Cron Jobs
> *"/cron add 'daily_standup' every 9h 'Check my goals and send morning briefing'"*

Schedule the agent to run any task on a schedule. It runs the task with full tool access and reports results back to your Telegram.

### 4. 🤖 Code & Deploy Assistant
> *"Deploy the latest version and tell me if there are any errors"*

The agent runs your deploy script via `shell`, checks the logs, hits your health check endpoint, and reports success or failure — all from Telegram while you're on the go.

---

## 🔧 Advanced Configuration

### Adding Custom Tools

Create `tools/my_tool.py`:

```python
TOOL_DEFINITION = {
    "name": "my_tool",
    "description": "What this tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "..."}
        },
        "required": ["param"]
    }
}

def run(param: str) -> str:
    # Your implementation
    return result
```

Then register it in `core/agent.py`:
```python
from tools import my_tool
ALL_TOOLS = [..., my_tool.TOOL_DEFINITION]
```

### Cron Job Format

```json
{
  "abc123": {
    "name": "Morning Briefing",
    "schedule": "every 24h",
    "task": "Give me a morning briefing with my top 3 priorities",
    "enabled": true
  }
}
```

Supports: `every 30m`, `every 1h`, `every 2d`, or full cron syntax like `"0 9 * * 1-5"`

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

```bash
git clone https://github.com/DaveLee-fun/AgileClaw.git
cd AgileClaw
./setup.sh
```

**Ideas for contributions:**
- New tool integrations (Notion, Linear, Slack, etc.)
- New channel adapters (WhatsApp, Discord)
- Better memory compression for long-running agents
- Web UI for goal setting and KPI visualization

Please open an issue first to discuss major changes.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

Free to use, modify, and distribute. If AgileClaw helps your business, consider giving it a ⭐

---

<div align="center">

**Built with ❤️ by [DaveLee](https://github.com/DaveLee-fun)**

*Solo entrepreneur · 10+ years teaching tech · Building in public*

</div>
