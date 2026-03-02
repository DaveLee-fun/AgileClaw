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
    logger.info("AgileClaw starting...")

    # Initialize agent
    agent = Agent(config)
    logger.info("Agent initialized.")

    # Initialize scheduler
    scheduler = None
    if "cron" in config:
        def on_cron_trigger(job_name: str, task: str):
            logger.info(f"Cron triggered: {job_name}")
            response = agent.chat(task, chat_id="cron")
            # TODO: send response to Telegram if chat_id configured
            logger.info(f"Cron result: {response[:200]}")

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
        print("\nAgileClaw CLI mode (no Telegram configured)")
        print("Type 'quit' to exit, 'agile' for agile review\n")
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() == "quit":
                    break
                elif user_input.lower() == "agile":
                    response = agent.run_agile_review()
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
