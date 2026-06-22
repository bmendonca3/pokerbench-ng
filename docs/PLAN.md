# PokerBench-NG Plan

PokerBench-NG measures poker decision quality, execution reliability, and strategic robustness under partial information. It should be a credible benchmark, not merely a public bot tournament.

## MVP Scope

- Heads-up No-Limit Texas Hold'em first.
- 100bb effective stacks.
- Static EV-loss spot evaluation.
- Controlled rollouts against fixed bots.
- Strict JSON agent protocol.
- Local CLI evaluator.
- JSON and Markdown reports.

## Non-Goals

- Real-money poker.
- 6-max as the first core format.
- Hosted hidden evaluation before the local evaluator is stable.
- AIVAT/MIVAT before duplicate-hand rollouts.
- Reusing source from Commons Clause benchmark repositories.

## Tracks

1. Static EV-loss spot test.
2. Controlled rollout against fixed bots.
3. Public arena/stress test as secondary.
4. Separate model-only, agent, and tool-assisted classes.

