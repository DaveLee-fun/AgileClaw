"""
Telegram channel — receive messages and send responses.
Uses python-telegram-bot v20+ (async).
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
        self.app.add_handler(CommandHandler("agile", self._handle_agile))
        self.app.add_handler(CommandHandler("cron", self._handle_cron))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

    def _is_allowed(self, user_id: int) -> bool:
        return not self.allowed_users or user_id in self.allowed_users

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👋 AgileClaw ready!\n\n"
            "Commands:\n"
            "/agile — Run agile review\n"
            "/cron — Manage scheduled tasks\n"
            "\nJust send a message to talk to the agent."
        )

    async def _handle_agile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_user.id):
            return
        await update.message.reply_text("🔄 Running agile review...")
        chat_id = str(update.effective_chat.id)
        response = self.agent.run_agile_review(chat_id)
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
                    lines.append(f"{status} [{j['id']}] {j['name']} — {j['schedule']}")
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
