# Repository Scaffold

The evaluator core is Python. The optional web viewer is intentionally not an MVP blocker.

## Package Boundaries

- `engine/`: card, deck, rules, state, legal actions, transitions, showdown.
- `agents/`: protocol, validation, subprocess/Python/HTTP/model-only adapters.
- `bots/`: baseline agents using the same protocol as external agents.
- `static/`: spot loader, solver-label boundary, normalizer, EV-loss scorer.
- `rollout/`: match scheduler, duplicate-hand protocol, bb/100 scorer.
- `diagnostics/`: tags, axes, rollups, report sections.
- `reporting/`: JSON, Markdown, leaderboard artifacts.
- `security/`: future hosted-eval sandbox and execution limits.

## CLI Targets

- `pokerbench-ng validate-agent`
- `pokerbench-ng eval-static`
- `pokerbench-ng eval-rollout`
- `pokerbench-ng eval-suite`
- `pokerbench-ng report`
- `pokerbench-ng leaderboard`

