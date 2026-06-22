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

The local-first MVP is complete. The repo can validate the example agent, run static EV-loss evaluation over the toy public spot, run a controlled HUNL rollout against `CallCheckBot`, and emit metrics, Markdown, leaderboard, and run JSON artifacts.

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
