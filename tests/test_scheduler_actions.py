import json
import tempfile
import unittest
from pathlib import Path

from scheduler.cron import CronScheduler


class SchedulerActionTests(unittest.TestCase):
    def test_add_daily_report_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            jobs_file = Path(tmp) / "cron_jobs.json"
            scheduler = CronScheduler(jobs_file=str(jobs_file))

            scheduler.add_job(
                name="daily-report",
                schedule="every 1h",
                action="daily_report",
                chat_id="default",
            )
            jobs = scheduler.list_jobs()
            scheduler.stop()

            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0]["action"], "daily_report")

    def test_legacy_job_normalization(self):
        with tempfile.TemporaryDirectory() as tmp:
            jobs_file = Path(tmp) / "cron_jobs.json"
            legacy_jobs = {
                "legacy": {
                    "id": "legacy",
                    "name": "legacy-job",
                    "schedule": "0 9 * * *",
                    "task": "hello",
                }
            }
            jobs_file.write_text(json.dumps(legacy_jobs))

            scheduler = CronScheduler(jobs_file=str(jobs_file))
            jobs = scheduler.list_jobs()
            scheduler.stop()

            self.assertEqual(jobs[0]["action"], "chat")
            self.assertEqual(jobs[0]["message"], "hello")

    def test_invalid_jobs_file_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            jobs_file = Path(tmp) / "cron_jobs.json"
            jobs_file.write_text("{invalid json")

            scheduler = CronScheduler(jobs_file=str(jobs_file))
            jobs = scheduler.list_jobs()
            scheduler.stop()

            self.assertEqual(jobs, [])

    def test_add_job_rejects_invalid_schedule(self):
        with tempfile.TemporaryDirectory() as tmp:
            jobs_file = Path(tmp) / "cron_jobs.json"
            scheduler = CronScheduler(jobs_file=str(jobs_file))

            with self.assertRaises(ValueError):
                scheduler.add_job(
                    name="bad-schedule",
                    schedule="every 0m",
                    action="chat",
                    message="hello",
                )
            scheduler.stop()

    def test_invalid_persisted_schedule_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            jobs_file = Path(tmp) / "cron_jobs.json"
            jobs = {
                "bad": {
                    "id": "bad",
                    "name": "bad-schedule",
                    "schedule": "every 0m",
                    "action": "chat",
                    "message": "x",
                    "enabled": True,
                },
                "good": {
                    "id": "good",
                    "name": "good-schedule",
                    "schedule": "every 1h",
                    "action": "chat",
                    "message": "y",
                    "enabled": True,
                },
            }
            jobs_file.write_text(json.dumps(jobs))

            scheduler = CronScheduler(jobs_file=str(jobs_file))
            scheduled_ids = {job.id for job in scheduler.scheduler.get_jobs()}
            scheduler.stop()

            self.assertIn("good", scheduled_ids)
            self.assertNotIn("bad", scheduled_ids)


if __name__ == "__main__":
    unittest.main()
