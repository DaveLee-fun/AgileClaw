"""
Simple cron scheduler.
Jobs persist to cron_jobs.json.
Supports cron strings and interval strings like "every 1h", "every 30m".
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


class CronScheduler:
    def __init__(self, jobs_file: str = "./cron_jobs.json", on_trigger: Optional[Callable] = None):
        self.jobs_file = Path(jobs_file)
        self.on_trigger = on_trigger  # callback(job_name, task_message)
        self.scheduler = BackgroundScheduler()
        self._load_and_schedule()

    def _load_and_schedule(self):
        """Load persisted jobs and schedule them."""
        for job in self._load_jobs().values():
            if job.get("enabled", True):
                self._schedule_job(job)

    def _load_jobs(self) -> dict:
        if self.jobs_file.exists():
            with open(self.jobs_file) as f:
                return json.load(f)
        return {}

    def _save_jobs(self, jobs: dict):
        with open(self.jobs_file, "w") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)

    def _schedule_job(self, job: dict):
        """Add job to APScheduler."""
        schedule = job["schedule"]
        job_id = job["id"]

        def trigger_fn():
            if self.on_trigger:
                self.on_trigger(job["name"], job["task"])

        # Parse schedule
        if schedule.startswith("every "):
            # e.g. "every 1h", "every 30m", "every 2d"
            val = schedule[6:]
            if val.endswith("h"):
                trigger = IntervalTrigger(hours=int(val[:-1]))
            elif val.endswith("m"):
                trigger = IntervalTrigger(minutes=int(val[:-1]))
            elif val.endswith("d"):
                trigger = IntervalTrigger(days=int(val[:-1]))
            else:
                trigger = IntervalTrigger(seconds=int(val))
        else:
            # Treat as cron string
            trigger = CronTrigger.from_crontab(schedule)

        self.scheduler.add_job(trigger_fn, trigger, id=job_id, replace_existing=True)

    def add_job(self, name: str, schedule: str, task: str, chat_id: str = None) -> str:
        """Add a new cron job. Returns job ID."""
        job_id = str(uuid.uuid4())[:8]
        job = {
            "id": job_id,
            "name": name,
            "schedule": schedule,
            "task": task,
            "chat_id": chat_id,
            "enabled": True,
            "created_at": datetime.now().isoformat(),
        }
        jobs = self._load_jobs()
        jobs[job_id] = job
        self._save_jobs(jobs)
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
        return list(self._load_jobs().values())

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
