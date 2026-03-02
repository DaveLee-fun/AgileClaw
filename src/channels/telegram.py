"""
Telegram channel — receive messages and send responses.
Uses python-telegram-bot v20+ (async).
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from core.version import __version__

logger = logging.getLogger(__name__)


class TelegramChannel:
    def __init__(self, bot_token: str, allowed_users: list[int], agent):
        self.bot_token = bot_token
        self.allowed_users = set(allowed_users)
        self.agent = agent
        self.app = Application.builder().token(bot_token).build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(CommandHandler("goal", self._handle_goal))
        self.app.add_handler(CommandHandler("teams", self._handle_teams))
        self.app.add_handler(CommandHandler("agile", self._handle_agile))
        self.app.add_handler(CommandHandler("report", self._handle_report))
        self.app.add_handler(CommandHandler("skills", self._handle_skills))
        self.app.add_handler(CommandHandler("runskill", self._handle_runskill))
        self.app.add_handler(CommandHandler("cron", self._handle_cron))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

    def _is_allowed(self, user_id: int) -> bool:
        return not self.allowed_users or user_id in self.allowed_users

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"👋 AgileClaw v{__version__} ready!\n\n"
            "Commands:\n"
            "/goal <name> | <objective> [| <kpi_hint>] — Create Agile Team for goal\n"
            "/teams — List Agile Teams\n"
            "/agile — Run agile review\n"
            "/report [daily|weekly] — Generate KPI report\n"
            "/skills — List installed skills\n"
            "/runskill — Execute a skill\n"
            "/cron — Manage scheduled tasks\n"
            "\nJust send a message to talk to the agent."
        )

    async def _handle_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_user.id):
            return

        raw = " ".join(context.args).strip()
        if not raw:
            await update.message.reply_text(
                "Usage: /goal <goal_name> | <objective> [| <kpi_hint>]\n"
                "Example: /goal 3월 매출 증가 | 3월 말까지 일매출 300달러 달성 | 결제 대시보드 기준"
            )
            return

        parts = [part.strip() for part in raw.split("|")]
        if len(parts) < 2:
            await update.message.reply_text(
                "Usage: /goal <goal_name> | <objective> [| <kpi_hint>]"
            )
            return

        goal_name = parts[0]
        objective = parts[1]
        kpi_hint = parts[2] if len(parts) > 2 else ""

        await update.message.reply_text(f"🎯 Setting up Agile Team: {goal_name}")
        chat_id = str(update.effective_chat.id)
        response = self.agent.create_agile_team(
            goal_name=goal_name,
            objective=objective,
            kpi_hint=kpi_hint,
            chat_id=chat_id,
        )
        await update.message.reply_text(response)

    async def _handle_teams(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_user.id):
            return

        teams = self.agent.list_agile_teams()
        if not teams:
            await update.message.reply_text("No Agile Teams yet. Use /goal to create one.")
            return

        lines = ["👥 Agile Teams:"]
        for team in teams:
            lines.append(f"- {team['team_id']}: {team['goal_name']}")
        await update.message.reply_text("\n".join(lines))

    async def _handle_agile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_user.id):
            return
        await update.message.reply_text("🔄 Running agile review...")
        chat_id = str(update.effective_chat.id)
        response = self.agent.run_agile_review(chat_id)
        await update.message.reply_text(response)

    async def _handle_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_user.id):
            return

        mode = (context.args[0].lower() if context.args else "daily").strip()
        chat_id = str(update.effective_chat.id)
        if mode == "weekly":
            await update.message.reply_text("🧾 Running weekly KPI report...")
            response = self.agent.run_weekly_report(chat_id)
        elif mode == "daily":
            await update.message.reply_text("🧾 Running daily KPI report...")
            response = self.agent.run_daily_report(chat_id)
        else:
            await update.message.reply_text("Usage: /report [daily|weekly]")
            return

        await update.message.reply_text(response)

    async def _handle_skills(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_user.id):
            return
        skills = self.agent.list_skills()
        if not skills:
            await update.message.reply_text("No local skills found in skills/*/SKILL.md")
            return

        lines = ["🧩 Installed skills:"]
        for skill in skills:
            lines.append(f"- {skill['key']}: {skill['description']}")
        await update.message.reply_text("\n".join(lines))

    async def _handle_runskill(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_user.id):
            return
        if not context.args:
            await update.message.reply_text(
                "Usage: /runskill <skill_key> [instruction]\nExample: /runskill agile-weekly-review 이번 주 KPI 리뷰해줘"
            )
            return

        skill_key = context.args[0]
        instruction = " ".join(context.args[1:]).strip()
        await update.message.reply_text(f"🔧 Running skill: {skill_key}")
        chat_id = str(update.effective_chat.id)
        response = self.agent.run_skill(skill_key, instruction, chat_id=chat_id)
        await update.message.reply_text(response)

    async def _handle_cron(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_user.id):
            return
        # Show cron job list
        if hasattr(self.agent, 'scheduler') and self.agent.scheduler:
            jobs = self.agent.scheduler.list_jobs()
            if not jobs:
                await update.message.reply_text("No cron jobs scheduled.")
            else:
                lines = ["📅 Cron Jobs:"]
                for j in jobs:
                    status = "✅" if j.get("enabled") else "⏸"
                    action = j.get("action", "chat")
                    extra = f", skill={j.get('skill')}" if action == "run_skill" and j.get("skill") else ""
                    lines.append(f"{status} [{j['id']}] {j['name']} — {j['schedule']} ({action}{extra})")
                await update.message.reply_text("\n".join(lines))
        else:
            await update.message.reply_text("Scheduler not initialized.")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_user.id):
            return
        user_message = update.message.text
        chat_id = str(update.effective_chat.id)

        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        try:
            response = self.agent.chat(user_message, chat_id)
            # Split long messages (Telegram limit: 4096 chars)
            if len(response) > 4000:
                for i in range(0, len(response), 4000):
                    await update.message.reply_text(response[i:i+4000])
            else:
                await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(f"Error: {e}")

    async def send_message(self, chat_id: str, text: str):
        """Send a proactive message (e.g., from cron jobs)."""
        await self.app.bot.send_message(chat_id=chat_id, text=text)

    def run(self):
        """Start the bot (blocking)."""
        logger.info("Starting Telegram bot...")
        self.app.run_polling(drop_pending_updates=True)
