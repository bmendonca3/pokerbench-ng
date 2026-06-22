# PokerBench-NG

PokerBench-NG is a clean-room, local-first benchmark for evaluating AI and LLM poker play in No-Limit Texas Hold'em.

The project prioritizes credible measurement over flashy tournament rankings. The MVP target combines:

- static EV-loss spot evaluation,
- controlled heads-up no-limit hold'em rollouts against fixed bots,
- strict JSON agent protocol,
- separate model-only, agent, and tool-assisted tracks,
- JSON/Markdown reports with reproducibility metadata.

## Current Status

This repository is in bootstrap stage. The first working slice provides the package layout, CLI, starter protocol models, card/deck primitives, example agent, and standard-library tests.

## Quickstart

```bash
python3 -m pip install -e ".[dev]"
pokerbench-ng --help
pokerbench-ng validate-agent examples/agents/python_random_agent/agent.yaml
python3 -m unittest discover -s tests
```

## Clean-Room Boundary

PokerBench-NG may interoperate with public run formats later, but implementation code should be independently written. Do not copy source from Commons Clause or other license-restricted benchmark repositories.

## Documentation

- `docs/PLAN.md`: benchmark thesis, scope, and track boundaries.
- `docs/SCAFFOLD.md`: repository layout and module responsibilities.
- `docs/TODO.md`: prioritized implementation checklist.
- `docs/IMPLEMENTATION_BRIEF.md`: first engineering tickets and acceptance criteria.

