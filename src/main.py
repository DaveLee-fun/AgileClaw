"""
AgileClaw — Entry point.

Usage:
  python main.py              # Start with config.yaml
  python main.py --config /path/to/config.yaml
"""
import argparse
import logging
import yaml
from pathlib import Path

from core.agent import Agent
from core.version import __version__
from channels.telegram import TelegramChannel
from scheduler.cron import CronScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agileclaw")


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="AgileClaw — Personal AI Agent")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        print(f"Copy config.example.yaml to config.yaml and fill in your credentials.")
        return

    config = load_config(config_path)
    logger.info("AgileClaw starting... version=%s", __version__)

    # Initialize agent
    agent = Agent(config)
    logger.info("Agent initialized.")

    # Initialize scheduler
    scheduler = None
    channel = None
    if "cron" in config:
        def on_cron_trigger(job: dict):
            job_name = job.get("name", "(unnamed)")
            action = job.get("action", "chat")
            chat_id = str(job.get("chat_id") or "cron")
            logger.info(f"Cron triggered: {job_name} ({action})")

            try:
                if action == "agile_review":
                    response = agent.run_agile_review(chat_id=chat_id)
                elif action == "daily_report":
                    response = agent.run_daily_report(chat_id=chat_id)
                elif action == "weekly_report":
                    response = agent.run_weekly_report(chat_id=chat_id)
                elif action == "run_skill":
                    skill = job.get("skill", "")
                    message = job.get("message", "")
                    response = agent.run_skill(skill, message, chat_id=chat_id)
                else:
                    # Backward compatible: support old 'task' field
                    message = job.get("message") or job.get("task") or ""
                    if not message.strip():
                        logger.warning(f"Cron chat job has empty message: {job_name}")
                        return
                    response = agent.chat(message, chat_id=chat_id)
                logger.info(f"Cron result: {response[:200]}")
            except Exception as exc:
                logger.exception(f"Cron job failed: {job_name} ({exc})")

        scheduler = CronScheduler(
            jobs_file=config["cron"]["jobs_file"],
            on_trigger=on_cron_trigger,
        )
        agent.scheduler = scheduler
        scheduler.start()
        logger.info("Scheduler started.")

    # Start Telegram channel
    if "telegram" in config:
        channel = TelegramChannel(
            bot_token=config["telegram"]["bot_token"],
            allowed_users=config["telegram"].get("allowed_users", []),
            agent=agent,
        )
        logger.info("Starting Telegram bot...")
        channel.run()  # blocking
    else:
        logger.warning("No channel configured. Add 'telegram' to config.yaml.")
        # Interactive CLI fallback
        print(f"\nAgileClaw v{__version__} CLI mode (no Telegram configured)")
        print("Type 'quit' to exit, 'agile' for agile review, 'skills' to list skills")
        print("Type: skill <skill_key> [instruction]")
        print("Type: goal <name> | <objective> [| <kpi_hint>]")
        print("Type: teams\n")
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() == "quit":
                    break
                elif user_input.lower() == "agile":
                    response = agent.run_agile_review()
                elif user_input.lower() == "skills":
                    skills = agent.list_skills()
                    if skills:
                        lines = [f"- {s['key']}: {s['description']}" for s in skills]
                        response = "Installed skills:\n" + "\n".join(lines)
                    else:
                        response = "No local skills found."
                elif user_input.lower() == "teams":
                    teams = agent.list_agile_teams()
                    if teams:
                        lines = [f"- {t['team_id']}: {t['goal_name']}" for t in teams]
                        response = "Agile Teams:\n" + "\n".join(lines)
                    else:
                        response = "No Agile Teams yet. Use: goal <name> | <objective>"
                elif user_input.lower().startswith("goal "):
                    raw = user_input[5:].strip()
                    parts = [part.strip() for part in raw.split("|")]
                    if len(parts) < 2:
                        response = "Usage: goal <name> | <objective> [| <kpi_hint>]"
                    else:
                        goal_name = parts[0]
                        objective = parts[1]
                        kpi_hint = parts[2] if len(parts) > 2 else ""
                        response = agent.create_agile_team(
                            goal_name=goal_name,
                            objective=objective,
                            kpi_hint=kpi_hint,
                        )
                elif user_input.lower().startswith("skill "):
                    parts = user_input.split(maxsplit=2)
                    skill_name = parts[1] if len(parts) > 1 else ""
                    instruction = parts[2] if len(parts) > 2 else ""
                    response = agent.run_skill(skill_name, instruction)
                else:
                    response = agent.chat(user_input)
                print(f"Agent: {response}\n")
            except (KeyboardInterrupt, EOFError):
                break

    if scheduler:
        scheduler.stop()
    logger.info("AgileClaw stopped.")


if __name__ == "__main__":
    main()
