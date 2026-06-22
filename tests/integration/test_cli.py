import json
import unittest
import tempfile
from pathlib import Path

from pokerbench_ng.cli import main


class CliTests(unittest.TestCase):
    def test_help_exits_zero(self):
        self.assertEqual(main([]), 0)

    def test_version_exits_zero(self):
        self.assertEqual(main(["--version"]), 0)

    def test_validate_agent_exits_zero(self):
        self.assertEqual(main(["validate-agent", "examples/agents/python_random_agent/agent.yaml"]), 0)

    def test_eval_static_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            status = main(
                [
                    "eval-static",
                    "--agent",
                    "examples/agents/python_random_agent/agent.yaml",
                    "--spots",
                    "src/pokerbench_ng/data/public_spots/dev.example.jsonl",
                    "--out-dir",
                    tmpdir,
                ]
            )
            self.assertEqual(status, 0)
            files = {path.suffix for path in Path(tmpdir).iterdir()}
            self.assertIn(".json", files)
            self.assertIn(".md", files)
            metrics = next(Path(tmpdir).glob("*.metrics.json"))
            data = json.loads(metrics.read_text(encoding="utf-8"))
            reproducibility = data["reproducibility"]
            self.assertIn("agent_manifest_hash", reproducibility)
            self.assertIn("spots", reproducibility["inputs"])
            leaderboard = next(Path(tmpdir).glob("*.leaderboard.json"))
            leaderboard_data = json.loads(leaderboard.read_text(encoding="utf-8"))
            self.assertEqual(leaderboard_data["reproducibility"], reproducibility)

    def test_eval_rollout_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as report_dir, tempfile.TemporaryDirectory() as run_dir:
            status = main(
                [
                    "eval-rollout",
                    "--agent",
                    "examples/agents/python_random_agent/agent.yaml",
                    "--config",
                    "configs/mvp_hunl_rollout.yaml",
                    "--hands",
                    "2",
                    "--out-dir",
                    report_dir,
                    "--runs-dir",
                    run_dir,
                ]
            )
            self.assertEqual(status, 0)
            self.assertTrue(list(Path(report_dir).glob("*.metrics.json")))
            run_json = next(Path(run_dir).glob("*.json"))
            self.assertTrue(run_json)
            run_data = json.loads(run_json.read_text(encoding="utf-8"))
            self.assertTrue(
                any(hand["seat_assignment"]["agent"] == "BB" for hand in run_data["hands"])
            )
            self.assertIn("seed_schedule_hash", run_data["reproducibility"])
            metrics = next(Path(report_dir).glob("*.metrics.json"))
            metrics_data = json.loads(metrics.read_text(encoding="utf-8"))
            self.assertEqual(run_data["reproducibility"], metrics_data["reproducibility"])
            leaderboard = next(Path(report_dir).glob("*.leaderboard.json"))
            leaderboard_data = json.loads(leaderboard.read_text(encoding="utf-8"))
            self.assertEqual(leaderboard_data["reproducibility"], metrics_data["reproducibility"])

    def test_report_and_leaderboard_commands(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            status = main(
                [
                    "eval-static",
                    "--agent",
                    "examples/agents/python_random_agent/agent.yaml",
                    "--spots",
                    "src/pokerbench_ng/data/public_spots/dev.example.jsonl",
                    "--out-dir",
                    tmpdir,
                ]
            )
            self.assertEqual(status, 0)
            metrics = next(Path(tmpdir).glob("*.metrics.json"))
            self.assertEqual(main(["report", str(metrics)]), 0)
            self.assertEqual(main(["leaderboard", str(metrics), "--agent-name", "Example"]), 0)


if __name__ == "__main__":
    unittest.main()
