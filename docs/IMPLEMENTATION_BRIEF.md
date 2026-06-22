# Implementation Brief

## Objective

Build PokerBench-NG as a local-first, clean-room benchmark for AI/LLM No-Limit Texas Hold'em play.

The first deliverable is a working MVP that can:

1. Validate an agent.
2. Run static EV-loss evaluation.
3. Run controlled HUNL rollouts.
4. Produce JSON and Markdown reports.
5. Reproduce results from seeds and config hashes.

## Current Slice

The local-first MVP seed repo is implemented. The repo can validate the example agent, run static EV-loss evaluation over the toy public spot, run a controlled HUNL smoke rollout against `CallCheckBot`, and emit metrics, Markdown, leaderboard, and run JSON artifacts with reproducibility metadata.

This is not a benchmark-quality release yet. The current artifacts prove evaluator plumbing and report generation. They do not establish leaderboard stability, solver-grade coverage, hidden evaluation integrity, or opponent robustness.

Verified local commands:

```bash
python3 -m pip install -e ".[dev]"
pokerbench-ng validate-agent examples/agents/python_random_agent/agent.yaml
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

## Next Ticket

Optional hardening ticket:

- add a larger public dev spot set,
- validate schemas with `jsonschema`,
- add more fixed opponents,
- improve rollout confidence intervals and duplicate-hand support,
- add a Git repo/CI pass if publishing.

Acceptance:

```bash
python3 -m unittest discover -s tests
python3 -m compileall src tests
```
