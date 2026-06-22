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
