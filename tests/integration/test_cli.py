import json
import unittest
import tempfile
from pathlib import Path

from pokerbench_ng.cli import main
from pokerbench_ng.reporting.schema_validation import validate_schema


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

    def test_eval_rollout_accepts_fixed_opponents(self):
        for opponent in ("always_fold", "random_legal"):
            with self.subTest(opponent=opponent):
                with tempfile.TemporaryDirectory() as report_dir, tempfile.TemporaryDirectory() as run_dir:
                    status = main(
                        [
                            "eval-rollout",
                            "--agent",
                            "examples/agents/python_random_agent/agent.yaml",
                            "--config",
                            "configs/mvp_hunl_rollout.yaml",
                            "--hands",
                            "4",
                            "--opponent",
                            opponent,
                            "--out-dir",
                            report_dir,
                            "--runs-dir",
                            run_dir,
                        ]
                    )
                    self.assertEqual(status, 0)
                    metrics = json.loads(next(Path(report_dir).glob("*.metrics.json")).read_text(encoding="utf-8"))
                    run_data = json.loads(next(Path(run_dir).glob("*.json")).read_text(encoding="utf-8"))
                    self.assertEqual(metrics["opponent"]["id"], opponent)
                    self.assertEqual(run_data["opponent"]["id"], opponent)
                    self.assertEqual(metrics["reproducibility"]["opponent"]["id"], opponent)

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

    def test_generated_artifacts_validate_against_committed_schemas(self):
        with tempfile.TemporaryDirectory() as static_report_dir:
            status = main(
                [
                    "eval-static",
                    "--agent",
                    "examples/agents/python_random_agent/agent.yaml",
                    "--spots",
                    "src/pokerbench_ng/data/public_spots/dev.example.jsonl",
                    "--out-dir",
                    static_report_dir,
                ]
            )
            self.assertEqual(status, 0)
            static_checks = [
                (next(Path(static_report_dir).glob("*.metrics.json")), Path("schemas/metrics.schema.json")),
                (next(Path(static_report_dir).glob("*.leaderboard.json")), Path("schemas/leaderboard.schema.json")),
            ]
            for artifact_path, schema_path in static_checks:
                with self.subTest(artifact=artifact_path.name):
                    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
                    schema = json.loads(schema_path.read_text(encoding="utf-8"))
                    self.assertEqual(validate_schema(artifact, schema), [])

        with tempfile.TemporaryDirectory() as report_dir, tempfile.TemporaryDirectory() as run_dir:
            status = main(
                [
                    "eval-rollout",
                    "--agent",
                    "examples/agents/python_random_agent/agent.yaml",
                    "--config",
                    "configs/mvp_hunl_rollout.yaml",
                    "--hands",
                    "4",
                    "--out-dir",
                    report_dir,
                    "--runs-dir",
                    run_dir,
                ]
            )
            self.assertEqual(status, 0)
            checks = [
                (next(Path(report_dir).glob("*.metrics.json")), Path("schemas/metrics.schema.json")),
                (next(Path(report_dir).glob("*.leaderboard.json")), Path("schemas/leaderboard.schema.json")),
                (next(Path(run_dir).glob("*.json")), Path("schemas/run_record.schema.json")),
            ]
            for artifact_path, schema_path in checks:
                with self.subTest(artifact=artifact_path.name):
                    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
                    schema = json.loads(schema_path.read_text(encoding="utf-8"))
                    self.assertEqual(validate_schema(artifact, schema), [])


if __name__ == "__main__":
    unittest.main()
