"""
Simple cron scheduler.
Jobs persist to cron_jobs.json.
Supports cron strings and interval strings like "every 1h", "every 30m".
"""
import json
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class CronScheduler:
    def __init__(self, jobs_file: str = "./cron_jobs.json", on_trigger: Optional[Callable] = None):
        self.jobs_file = Path(jobs_file)
        self.on_trigger = on_trigger  # callback(job: dict)
        self.scheduler = BackgroundScheduler()
        self._load_and_schedule()

    def _load_and_schedule(self):
        """Load persisted jobs and schedule them."""
        for raw_job in self._load_jobs().values():
            job = self._normalize_job(raw_job)
            if not job.get("enabled", True):
                continue
            if not job.get("id") or not job.get("schedule"):
                logger.warning("Skipping invalid cron job (missing id/schedule): %s", job)
                continue
            try:
                self._schedule_job(job)
            except Exception as exc:
                logger.warning("Skipping cron job %s due to schedule error: %s", job.get("id"), exc)

    def _load_jobs(self) -> dict:
        if self.jobs_file.exists():
            try:
                with open(self.jobs_file) as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
                logger.warning("jobs file is not a JSON object: %s", self.jobs_file)
                return {}
            except Exception as exc:
                logger.warning("Failed to load jobs file %s: %s", self.jobs_file, exc)
                return {}
        return {}

    def _save_jobs(self, jobs: dict):
        self.jobs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.jobs_file, "w") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _normalize_job(job: dict) -> dict:
        normalized = dict(job)
        if "message" not in normalized and "task" in normalized:
            normalized["message"] = normalized["task"]
        if "action" not in normalized:
            normalized["action"] = "chat"
        if "enabled" not in normalized:
            normalized["enabled"] = True
        return normalized

    @staticmethod
    def _parse_trigger(schedule: str):
        schedule_text = (schedule or "").strip()
        if not schedule_text:
            raise ValueError("Schedule cannot be empty")

        lowered = schedule_text.lower()
        if lowered.startswith("every "):
            # e.g. "every 1h", "every 30m", "every 2d", "every 45"
            val = schedule_text[6:].strip()
            match = re.fullmatch(r"(\d+)\s*([hmds]?)", val, flags=re.IGNORECASE)
            if not match:
                raise ValueError(f"Invalid interval schedule: {schedule_text}")
            amount = int(match.group(1))
            unit = (match.group(2) or "s").lower()
            if amount <= 0:
                raise ValueError(f"Interval must be > 0: {schedule_text}")
            if unit == "h":
                return IntervalTrigger(hours=amount)
            if unit == "m":
                return IntervalTrigger(minutes=amount)
            if unit == "d":
                return IntervalTrigger(days=amount)
            return IntervalTrigger(seconds=amount)

        # Treat as cron string
        return CronTrigger.from_crontab(schedule_text)

    def _schedule_job(self, job: dict):
        """Add job to APScheduler."""
        schedule = job["schedule"]
        job_id = job["id"]

        def trigger_fn():
            if self.on_trigger:
                self.on_trigger(dict(job))

        trigger = self._parse_trigger(schedule)
        self.scheduler.add_job(trigger_fn, trigger, id=job_id, replace_existing=True)

    def add_job(
        self,
        name: str,
        schedule: str,
        action: str = "chat",
        message: str = "",
        skill: str = "",
        chat_id: str = None,
        enabled: bool = True,
    ) -> str:
        """
        Add a new cron job. Returns job ID.

        Actions:
          - chat: send message to Agent.chat
          - agile_review: run Agent.run_agile_review
          - daily_report: run Agent.run_daily_report
          - weekly_report: run Agent.run_weekly_report
          - run_skill: run Agent.run_skill(skill, message)
        """
        # Validate schedule before persisting the job.
        self._parse_trigger(schedule)

        job_id = str(uuid.uuid4())[:8]
        job = {
            "id": job_id,
            "name": name,
            "schedule": schedule,
            "action": action,
            "message": message,
            "skill": skill,
            "chat_id": chat_id,
            "enabled": enabled,
            "created_at": datetime.now().isoformat(),
        }
        jobs = self._load_jobs()
        jobs[job_id] = job
        self._save_jobs(jobs)
        if enabled:
            self._schedule_job(job)
        return job_id

    def remove_job(self, job_id: str) -> bool:
        jobs = self._load_jobs()
        if job_id not in jobs:
            return False
        del jobs[job_id]
        self._save_jobs(jobs)
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass
        return True

    def list_jobs(self) -> list[dict]:
        return [self._normalize_job(job) for job in self._load_jobs().values()]

    def start(self):
        self.scheduler.start()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
