# PokerBench-NG To-Do

## MVP P0

- [x] Initialize repository skeleton.
- [x] Add package metadata and CLI entrypoint.
- [x] Add starter docs, examples, and tests.
- [x] Implement starter HUNL engine transitions with conservation tests.
- [x] Add full showdown hand evaluation and payout.
- [x] Implement strict agent request/response JSON Schema files.
- [x] Make Python/subprocess adapters execute real decisions.
- [x] Implement AlwaysFold, CallCheck, and RandomLegal against full request protocol.
- [x] Implement static EV-loss evaluator over toy/dev spots.
- [x] Implement controlled rollout evaluator with seed manifest and run JSONL.
- [x] Generate JSON/Markdown reports.

## MVP Done When

- [x] `pip install -e ".[dev]"` works.
- [x] `pokerbench-ng validate-agent examples/agents/python_random_agent/agent.yaml` works.
- [x] `pokerbench-ng eval-static ...` emits metrics JSON.
- [x] `pokerbench-ng eval-rollout ...` emits run JSONL and bb/100.
- [x] `python3 -m unittest discover -s tests` passes.

## Consultant Hardening

- [x] Enforce legal action type, call amount, and bet/raise bounds before engine application.
- [x] Preserve timeout, malformed, process-error, and illegal classifications in static and rollout metrics.
- [x] Make rollout seat assignment explicit and alternate submitted-agent SB/BB seats in smoke runs.
- [x] Add reproducibility metadata to metrics, run JSON, and leaderboard entries.
- [x] Align README and evidence wording with toy static spot and smoke rollout scope.

## MVP/v1 Seed Follow-Up

- [x] Add visible GitHub Actions gate and README badge after green run.
- [x] Expand the public toy static suite from 1 spot to at least 20 hand-authored toy spots.
- [x] Add rollout opponent selection for `call_check`, `always_fold`, and `random_legal`.
- [x] Add committed schema validation for emitted metrics, run, and leaderboard artifacts.
- [x] Add engine regression coverage for short-stack all-in calls, min/max raises, under-raises, bet/call closure, and river all-in showdown.
