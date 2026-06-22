# MVP Evidence Snapshots

These files are committed snapshots from the local-first MVP seed repo.

They show that PokerBench-NG can:

- validate the example Python random agent,
- evaluate the 20-spot hand-authored toy public static suite,
- run a controlled HUNL smoke rollout against `CallCheckBot`,
- emit metrics JSON, Markdown reports, leaderboard entries, and run JSON,
- include reproducibility metadata in generated artifacts.

They do not prove benchmark-quality coverage, leaderboard stability, hidden-set
integrity, or solver-grade evaluation.

Regeneration commands:

```bash
python3 -m pip install -e ".[dev]"
pokerbench-ng eval-static \
  --agent examples/agents/python_random_agent/agent.yaml \
  --spots src/pokerbench_ng/data/public_spots/dev.example.jsonl
pokerbench-ng eval-rollout \
  --agent examples/agents/python_random_agent/agent.yaml \
  --config configs/mvp_hunl_rollout.yaml \
  --hands 20
python3 -m unittest discover -s tests
python3 -m compileall src tests
```
