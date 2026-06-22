# PokerBench-NG Actionable Build Loop

## Current Status
Status: complete
Updated: 2026-06-21 17:45:38 MST
Next action: Optional follow-up only: harden the MVP with richer datasets, stricter JSON Schema validation, and broader rollout opponents.

## Contract
- Outcome: PokerBench-NG becomes an actionable, evidence-driven implementation project: a clean-room local evaluator MVP can validate an agent, run static EV-loss evaluation, run controlled HUNL rollouts, emit JSON/Markdown reports, and reproduce results from seeds/config hashes.
- Enhanced prompt:

  Improve the PokerBench-NG planning bundle so it drives implementation of a credible open AI poker benchmark. Start by converting the scaffold into a clean repo with deterministic Python package structure, strict JSON agent protocol placeholders, HUNL engine skeleton, baseline-bot interfaces, static/rollout evaluator entrypoints, docs, and tests. Preserve clean-room separation from Commons Clause code and keep arena play secondary to scientific scoring. Verify each milestone with executable commands and recorded artifacts.

- Context: Implementation repo lives at `/Users/brianmendonca/Documents/pokerbench-ng`. Source planning bundle lives at `/Users/brianmendonca/Documents/pokerbench-ng-artifact-pack`; zip artifact lives at `/Users/brianmendonca/Documents/pokerbench-ng-artifact-pack.zip`; ChatGPT consultant thread is `https://chatgpt.com/c/6a383a82-c998-832f-9ee4-5e6a5db3930f`.
- Boundaries: Work in this local repo and the planning bundle. Do not copy source code from `JoeAzar/pokerbench`; only use feature-level inspiration and independently written implementation. Do not create GitHub repos, push branches, open PRs, use paid APIs, or run external hosted evaluations without explicit user instruction.
- Constraints: Keep MVP local-first; HUNL before 6-max; static EV-loss and controlled rollout before public arena; model-only, agent, and tool-assisted tracks must stay separate; hidden evaluation and AIVAT/MIVAT are v1/v2 roadmap items, not MVP blockers; no secrets, solver licenses, private datasets, or tokens in docs.
- Verification:
  - Fast loop: `.venv/bin/python -m unittest discover -s tests`, `.venv/bin/python -m compileall src tests`, `.venv/bin/pokerbench-ng --help`.
  - Regression/control: review changed file list; ensure no copied third-party source; ensure `README.md`, `docs/PLAN.md`, `docs/TODO.md`, and `docs/IMPLEMENTATION_BRIEF.md` remain consistent.
  - Final MVP gate: `.venv/bin/python -m pip install -e ".[dev]"`, `.venv/bin/pokerbench-ng validate-agent examples/agents/python_random_agent/agent.yaml`, `pokerbench-ng eval-static ...`, `pokerbench-ng eval-rollout ...`, full tests, and generated metrics/report artifacts exist.
  - Evidence to save: command summaries, generated run/report paths, changed file list, and unresolved risks in this ledger.
- Iteration policy: Work one milestone at a time. Prefer the smallest executable vertical slice over broad scaffolding. After each attempt, update this file with result, evidence, and next action. If a check fails, fix the narrowest cause or record the blocker before expanding scope.
- Stop condition: Pause as blocked if the next milestone requires solver-labeled proprietary data, hosted hidden evaluation infrastructure, external model API credentials, GitHub publication, or a license decision that has not been approved by the user.

## Plan
- [x] Bootstrap clean local repo at `/Users/brianmendonca/Documents/pokerbench-ng`.
- [x] Add package skeleton, `pyproject.toml`, CLI entrypoint, docs, schemas, examples, and test directories from the scaffold.
- [x] Add starter card/deck primitives, legal-action model, agent manifest validation, baseline bot shells, static/rollout/reporting boundaries, and tests.
- [x] Implement starter card/deck/state primitives with deterministic shuffle and JSON serialization checks.
- [x] Implement starter HUNL legal-action generation and state transitions with conservation/property tests.
- [x] Add full showdown hand evaluation and payout.
- [x] Implement strict agent request/response schemas and Python/subprocess adapter stubs that execute real decisions.
- [x] Implement AlwaysFold, CallCheck, and RandomLegal baseline bots using the full request protocol.
- [x] Implement toy static evaluator with EV-loss scoring against public example spots.
- [x] Implement controlled rollout evaluator with seed manifest, run JSONL, bb/100, and bootstrap CI.
- [x] Implement JSON/Markdown reports and local leaderboard entry generation.
- [x] Run MVP final gate and record artifact paths.

## Attempt Ledger
### 2026-06-21 17:45:38 MST - MVP goal state completed
- Result: Completed the local-first MVP gate. PokerBench-NG can validate an agent, run static EV-loss evaluation, run controlled HUNL rollout, generate JSON/Markdown/leaderboard artifacts, and reproduce through the local `.venv` commands.
- Evidence:
  - Final gate command passed:
    - `.venv/bin/python -m pip install -e ".[dev]"`
    - `.venv/bin/pokerbench-ng validate-agent examples/agents/python_random_agent/agent.yaml`
    - `.venv/bin/pokerbench-ng eval-static --agent examples/agents/python_random_agent/agent.yaml --spots src/pokerbench_ng/data/public_spots/dev.example.jsonl`
    - `.venv/bin/pokerbench-ng eval-rollout --agent examples/agents/python_random_agent/agent.yaml --config configs/mvp_hunl_rollout.yaml --hands 5`
    - `.venv/bin/python -m unittest discover -s tests` ran 48 tests and passed.
    - `.venv/bin/python -m compileall src tests` passed.
  - Static artifacts:
    - `reports/static_1782089129651.metrics.json`
    - `reports/static_1782089129651.md`
    - `reports/static_1782089129651.leaderboard.json`
    - pushed-visible snapshot: `docs/evidence/mvp-final/static.metrics.json`
  - Rollout artifacts:
    - `reports/rollout_1782089130200.metrics.json`
    - `reports/rollout_1782089130200.md`
    - `reports/rollout_1782089130200.leaderboard.json`
    - `runs/rollout_1782089130200.json`
    - pushed-visible snapshot: `docs/evidence/mvp-final/rollout.metrics.json`
    - pushed-visible snapshot: `docs/evidence/mvp-final/rollout.run.json`
  - Static summary: 1 spot, EV loss 1.42 bb/decision, illegal/malformed rates 0.
  - Rollout summary: 5 hands, -190 bb/100 for the example random agent vs CallCheckBot, CI [-358.034996, -21.965004].
- Next action: Optional v1-hardening pass: add larger public dev data, stricter schema validation via `jsonschema`, more baseline opponents, and cleaner statistical rollout tests.

### 2026-06-21 17:30 MST - subagent delegation outcome
- Result: Spawned three GPT-5.5 low workers at the user's request. Worker A completed the protocol/adapters/bots slice and its changes were integrated. Workers B and C failed due workspace credits, so static/reporting and rollout were completed in the parent loop.
- Evidence:
  - Worker A changed `src/pokerbench_ng/agents/*`, `src/pokerbench_ng/bots/*`, `examples/agents/python_random_agent/agent.py`, and related tests.
  - Worker A verification: 17 focused tests passed in its report.
  - Parent verification after integration: full final gate above.
- Next action: None required for MVP completion.

### 2026-06-21 12:46:13 MST - starter HUNL transition slice verified
- Result: Implemented starter HUNL hand setup and transitions: blind posting, legal action generation, fold/call/check/bet/raise application, street advancement through river, fold terminal payout, showdown terminal boundary, and pot/stack conservation checks.
- Evidence:
  - `src/pokerbench_ng/engine/state.py`
  - `src/pokerbench_ng/engine/transitions.py`
  - `tests/property/test_engine_invariants.py`
  - `tests/unit/test_transitions.py`
  - `.venv/bin/python -m unittest tests.property.test_engine_invariants tests.unit.test_transitions` ran 8 tests and passed.
  - `.venv/bin/python -m unittest discover -s tests` ran 29 tests and passed.
  - `.venv/bin/pokerbench-ng --help` passed.
  - `.venv/bin/pokerbench-ng validate-agent examples/agents/python_random_agent/agent.yaml` passed.
- Next action: Implement protocol-driven baseline bot decisions and adapter execution for the example Python agent.

### 2026-06-21 12:43:00 MST - bootstrap repo scaffold verified
- Result: Created `/Users/brianmendonca/Documents/pokerbench-ng` as a clean-room implementation repo with package metadata, CLI, docs, schemas, configs, example agents, starter engine/protocol/bot/static/rollout/reporting modules, and 22 standard-library tests.
- Evidence:
  - `.venv/bin/python -m pip install -e ".[dev]"` passed after upgrading pip/setuptools inside the local `.venv`.
  - `.venv/bin/pokerbench-ng --help` passed.
  - `.venv/bin/pokerbench-ng validate-agent examples/agents/python_random_agent/agent.yaml` printed `valid agent manifest`.
  - `.venv/bin/python -m unittest discover -s tests` ran 22 tests and passed.
  - `.venv/bin/python -m compileall src tests` passed.
- Next action: Implement HUNL state transitions and conservation tests.

### 2026-06-21 12:35:03 MST - initialized persistent action loop
- Result: Created durable Goalcraft Persist contract for converting the ChatGPT-generated PokerBench-NG planning bundle into an executable local implementation project.
- Evidence:
  - `/Users/brianmendonca/Documents/pokerbench-ng-artifact-pack/BUNDLE_INDEX.md`
  - `/Users/brianmendonca/Documents/pokerbench-ng-artifact-pack/docs/TODO.md`
  - `/Users/brianmendonca/Documents/pokerbench-ng-artifact-pack/docs/IMPLEMENTATION_BRIEF.md`
  - `/Users/brianmendonca/Documents/pokerbench-ng-artifact-pack/_consultant/CHATGPT_ARTIFACT_PACK_RAW.md`
- Next action: Create the clean `pokerbench-ng` repo skeleton and verify `pip install -e ".[dev]"`, `pokerbench-ng --help`, and initial tests.

## Decisions And Assumptions
- Treat `/Users/brianmendonca/Documents/pokerbench-ng` as the active implementation repo and this file as the active state file.
- Keep `/Users/brianmendonca/Documents/pokerbench-ng-artifact-pack` as planning evidence and origin material.
- Prefer clean-room implementation over forking implementation code from Commons Clause sources; optional future compatibility can target run format import/export, not source reuse.
- MVP completion requires executable local evidence, not just docs.
- Public arena/replay UI is useful but secondary; do not let it displace EV-loss scoring, controlled rollout, or reliability metrics.
- AIVAT/MIVAT and hosted hidden evaluation remain v2/v1 roadmap items unless the user explicitly reprioritizes.
- No Codex `/goal` runtime is active for this work; this file is the durable state surface.

## Blockers
- None currently.
