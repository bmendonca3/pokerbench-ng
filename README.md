# PokerBench-NG

[![CI](https://github.com/bmendonca3/pokerbench-ng/actions/workflows/ci.yml/badge.svg)](https://github.com/bmendonca3/pokerbench-ng/actions/workflows/ci.yml)

PokerBench-NG is a clean-room, local-first seed repo for evaluating AI and LLM poker play in No-Limit Texas Hold'em.

The project is designed around credible measurement rather than flashy tournament rankings. The current local-first MVP seed implements:

- static EV-loss evaluation over a toy public spot,
- controlled heads-up no-limit hold'em smoke rollouts against `CallCheckBot`,
- strict JSON agent protocol,
- separate model-only, agent, and tool-assisted tracks,
- JSON/Markdown reports with reproducibility metadata.

## Current Status

The local-first MVP seed repo is implemented. It is useful for exercising package structure, the CLI, agent protocol boundaries, the starter HUNL engine slice, toy static scoring, smoke rollout plumbing, report generation, and reproducibility metadata.

It is not yet a benchmark-quality release. The public static dataset is intentionally tiny, hidden evaluation is not implemented, and rollout opponents are still starter baselines.

## Quickstart

```bash
python3 -m pip install -e ".[dev]"
pokerbench-ng --help
pokerbench-ng validate-agent examples/agents/python_random_agent/agent.yaml
pokerbench-ng eval-static \
  --agent examples/agents/python_random_agent/agent.yaml \
  --spots src/pokerbench_ng/data/public_spots/dev.example.jsonl
pokerbench-ng eval-rollout \
  --agent examples/agents/python_random_agent/agent.yaml \
  --config configs/mvp_hunl_rollout.yaml \
  --hands 20
python3 -m unittest discover -s tests
```

The committed MVP evidence snapshots in `docs/evidence/mvp-final/` were generated from the local toy static spot and a smoke rollout. They are proof of evaluator plumbing, not a stable leaderboard claim.

## Clean-Room Boundary

PokerBench-NG may interoperate with public run formats later, but implementation code should be independently written. Do not copy source from Commons Clause or other license-restricted benchmark repositories.

## Documentation

- `docs/PLAN.md`: benchmark thesis, scope, and track boundaries.
- `docs/SCAFFOLD.md`: repository layout and module responsibilities.
- `docs/SCHEMAS.md`: artifact schemas and reproducibility metadata.
- `docs/TODO.md`: prioritized implementation checklist.
- `docs/IMPLEMENTATION_BRIEF.md`: first engineering tickets and acceptance criteria.
