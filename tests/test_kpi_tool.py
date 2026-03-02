import json
import tempfile
import unittest

from tools import kpi


class KpiToolTests(unittest.TestCase):
    def test_upsert_log_list_metric(self):
        with tempfile.TemporaryDirectory() as tmp:
            upsert = kpi.upsert_metric(
                memory_dir=tmp,
                team_id="team-a",
                metric="daily_revenue",
                target=300,
                current=120,
                source="dashboard",
            )
            upsert_data = json.loads(upsert)
            self.assertEqual(upsert_data["status"], "upserted")

            logged = kpi.log_measurement(
                memory_dir=tmp,
                team_id="team-a",
                metric="daily_revenue",
                value=150,
                note="manual check",
            )
            log_data = json.loads(logged)
            self.assertEqual(log_data["status"], "logged")
            self.assertEqual(log_data["current"], 150)

            listed = kpi.list_metrics(memory_dir=tmp, team_id="team-a")
            list_data = json.loads(listed)
            self.assertEqual(list_data["metric_count"], 1)
            self.assertEqual(list_data["metrics"][0]["metric"], "daily_revenue")
            self.assertEqual(list_data["metrics"][0]["current"], 150)


if __name__ == "__main__":
    unittest.main()
