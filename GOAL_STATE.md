# PokerBench-NG Actionable Build Loop

## Current Status
Status: complete
Updated: 2026-06-21 23:23 MST
Next action: Optional follow-up only: continue with larger non-toy benchmark data design when desired.
Current source of truth: `/Users/brianmendonca/Documents/pokerbench-ng/GOAL_STATE.md`

## Contract
- Outcome: PokerBench-NG hardening pass addresses the ChatGPT Consultant MVP review so the repo remains an honest local-first MVP seed repo and removes the highest-risk correctness gaps before broader benchmark claims.
- Enhanced prompt:

  Improve the pushed PokerBench-NG seed repo by implementing the consultant's top MVP-hardening brief. Start with protocol legality: validate legal action type plus bet/raise bounds and supplied call amounts before engine application; preserve timeout/malformed/process/illegal classifications; use fallback actions for invalid agent responses; and prove the change with focused protocol, rollout, full test, compile, and CLI smoke checks. Then continue through reliability metrics, explicit seat assignment, reproducibility metadata, and README/evidence alignment unless a verification blocker appears.

- Context: Implementation repo lives at `/Users/brianmendonca/Documents/pokerbench-ng`; public repo is `https://github.com/bmendonca3/pokerbench-ng`; initial MVP commit is `5763e2e4f6a0b9013aa0f4b1580b3d1599ab65ba`; ChatGPT consultant thread is `https://chatgpt.com/c/6a383a82-c998-832f-9ee4-5e6a5db3930f`.
- Boundaries: Work in this local repo. Do not copy source code from `JoeAzar/pokerbench`; only use feature-level inspiration and independently written implementation. Do not use paid APIs, hosted hidden evaluations, or solver/private data. Pushing is allowed only when the user explicitly asks for it again or when a clear handoff requires publishing the completed local state.
- Constraints: Keep MVP local-first; HUNL before 6-max; static EV-loss and controlled rollout before public arena; model-only, agent, and tool-assisted tracks must stay separate; hidden evaluation and AIVAT/MIVAT are v1/v2 roadmap items, not MVP blockers; no secrets, solver licenses, private datasets, or tokens in docs.
- Verification:
  - Fast loop for item 1: `.venv/bin/python -m unittest tests.unit.test_protocol tests.integration.test_cli`; `.venv/bin/pokerbench-ng eval-rollout --agent examples/agents/python_random_agent/agent.yaml --config configs/mvp_hunl_rollout.yaml --hands 20`.
  - Regression/control: `.venv/bin/python -m unittest discover -s tests`, `.venv/bin/python -m compileall src tests`, changed-file review.
  - Final hardening gate: item-specific done-condition commands from the consultant brief plus full tests and compile pass.
  - Evidence to save: command summaries, generated run/report paths, changed file list, and unresolved risks in this ledger.
- Iteration policy: Work one milestone at a time. Prefer the smallest executable vertical slice over broad scaffolding. After each attempt, update this file with result, evidence, and next action. If a check fails, fix the narrowest cause or record the blocker before expanding scope.
- Stop condition: Pause as blocked if the next milestone requires solver-labeled proprietary data, hosted hidden evaluation infrastructure, external model API credentials, GitHub publication, or a license decision that has not been approved by the user.

## Plan
- [x] Item 1: Enforce full legal-action validation before rollout engine application.
- [x] Item 2: Add real reliability metrics to static and rollout reports.
- [x] Item 3: Make rollout seat assignment explicit and avoid SB-only scoring.
- [x] Item 4: Add minimal reproducibility metadata to reports/leaderboard.
- [x] Item 5: Align README and evidence language with toy/static smoke scope.
- [x] Previous MVP seed repo gate completed and pushed.

## Next Consultant Brief
- [x] Add visible GitHub Actions gate and README badge after green run.
- [x] Expand public toy static suite from 1 spot to 20-50 hand-authored toy spots.
- [x] Add rollout opponent selection for `call_check`, `always_fold`, and `random_legal`.
- [x] Add JSON Schema validation for emitted metrics/run/leaderboard artifacts.
- [x] Add engine regression cases for all-in and raise-edge behavior.

## Attempt Ledger
### 2026-06-21 23:23 MST - remaining consultant brief completed
- Result: Completed all remaining MVP/v1 seed brief items. Expanded the public static suite to 20 hand-authored toy spots, added rollout opponent selection for `call_check`, `always_fold`, and `random_legal`, added dependency-free schema validation for emitted metrics/run/leaderboard artifacts, and added engine regression coverage plus a fix for short-stack all-in calls and all-in street closure.
- Evidence:
  - Expanded static data: `src/pokerbench_ng/data/public_spots/dev.example.jsonl` now has 20 toy-labeled spots across preflop, flop, turn, and river.
  - Opponent CLI checks passed:
    - `.venv/bin/pokerbench-ng eval-rollout --agent examples/agents/python_random_agent/agent.yaml --config configs/mvp_hunl_rollout.yaml --hands 20 --opponent always_fold`
    - `.venv/bin/pokerbench-ng eval-rollout --agent examples/agents/python_random_agent/agent.yaml --config configs/mvp_hunl_rollout.yaml --hands 20 --opponent random_legal`
  - Static CLI check passed: `.venv/bin/pokerbench-ng eval-static --agent examples/agents/python_random_agent/agent.yaml --spots src/pokerbench_ng/data/public_spots/dev.example.jsonl`; generated `reports/static_1782109198730.metrics.json` with `static_spots: 20`.
  - Refreshed canonical evidence from `.venv/bin/pokerbench-ng eval-suite --agent examples/agents/python_random_agent/agent.yaml --suite mvp_hunl`:
    - `reports/static_1782109268591.metrics.json`
    - `reports/rollout_1782109268893.metrics.json`
    - `runs/rollout_1782109268893.json`
  - Evidence snapshots validated against committed schemas:
    - `docs/evidence/mvp-final/static.metrics.json`
    - `docs/evidence/mvp-final/static.leaderboard.json`
    - `docs/evidence/mvp-final/rollout.metrics.json`
    - `docs/evidence/mvp-final/rollout.leaderboard.json`
    - `docs/evidence/mvp-final/rollout.run.json`
  - Focused tests passed:
    - `.venv/bin/python -m unittest tests.unit.test_static_scorer tests.integration.test_cli` ran 14 tests and passed.
    - `.venv/bin/python -m unittest tests.unit.test_transitions tests.property.test_engine_invariants` ran 13 tests and passed.
  - Full regression pass: `.venv/bin/python -m unittest discover -s tests` ran 69 tests and passed.
  - Compile pass: `.venv/bin/python -m compileall src tests`.
  - Whitespace check: `git diff --check` passed.
- Publication:
  - Commit pushed to `main`: `91a5f3d1c9e695946a9f02d14ad0af8b815b0e02`.
  - GitHub Actions run passed: `https://github.com/bmendonca3/pokerbench-ng/actions/runs/27933837316`.
  - no-mistakes was initialized successfully and added the local `no-mistakes` remote. AXI validation did not complete: it refused `main` because it is the default branch, then failed on feature branch `validate-seed-follow-up` with `no run started for "validate-seed-follow-up": no previous run for branch validate-seed-follow-up`; `git push no-mistakes validate-seed-follow-up` reported `Everything up-to-date` but no run appeared. Local verification plus GitHub Actions were used as the final gate.
- Next action: Optional only; all requested remaining items are complete.

### 2026-06-21 20:38 MST - next brief item 1 visible CI completed
- Result: ChatGPT Consultant reviewed the pushed hardening commit and reported no blocker before continuing. GitHub Actions was already present and passed for the hardening commit, so the README badge was added and pushed. The latest badge commit also completed CI successfully.
- Evidence:
  - Consultant thread: `https://chatgpt.com/c/6a383a82-c998-832f-9ee4-5e6a5db3930f`
  - Hardening commit: `45224a5cc7aa76e8b2e5d1af2adc581e51cd6dcf`
  - README badge commit: `022966aeb7790c1f2d6008521e6db87e054894fc`
  - GitHub Actions run for badge commit: `https://github.com/bmendonca3/pokerbench-ng/actions/runs/27926045591`, conclusion `success`.
  - Local check before badge push: `git diff --check` passed.
  - Local regression before badge push: `.venv/bin/python -m unittest discover -s tests` ran 61 tests and passed.
  - no-mistakes gate status: `no-mistakes axi run` remains blocked because the repo is not initialized for no-mistakes (`repo not initialized (run 'no-mistakes init' first)`); local verification and GitHub Actions were used as fallback.
- Next action: Expand `src/pokerbench_ng/data/public_spots/dev.example.jsonl` to at least 20 explicitly toy-labeled spots and refresh static evidence.

### 2026-06-21 20:03 MST - item 5 README and evidence alignment completed
- Result: README and implementation brief now call the project a local-first MVP seed repo, describe the static dataset as a toy public spot, describe rollout as a smoke rollout against `CallCheckBot`, and explicitly avoid benchmark-quality release claims. Refreshed committed evidence snapshots from the latest verified run so they include reproducibility metadata and explicit seat assignments. Added `docs/evidence/mvp-final/README.md` to state what the snapshots prove and do not prove.
- Evidence:
  - Changed files:
    - `README.md`
    - `docs/IMPLEMENTATION_BRIEF.md`
    - `docs/TODO.md`
    - `docs/evidence/mvp-final/README.md`
    - `docs/evidence/mvp-final/static.metrics.json`
    - `docs/evidence/mvp-final/static.md`
    - `docs/evidence/mvp-final/static.leaderboard.json`
    - `docs/evidence/mvp-final/rollout.metrics.json`
    - `docs/evidence/mvp-final/rollout.md`
    - `docs/evidence/mvp-final/rollout.leaderboard.json`
    - `docs/evidence/mvp-final/rollout.run.json`
  - Evidence refresh assertion passed: static metrics, rollout metrics, and rollout run snapshots include `reproducibility`.
  - Wording check passed: `grep -R "hosted hidden\|AIVAT\|credible benchmark release" README.md docs/IMPLEMENTATION_BRIEF.md || true` returned no matches.
  - Full regression pass: `.venv/bin/python -m unittest discover -s tests` ran 61 tests and passed.
  - Compile pass: `.venv/bin/python -m compileall src tests`.
- Next action: Commit/push only if publication is desired; otherwise the local hardening pass is complete.

### 2026-06-21 20:00 MST - item 4 reproducibility metadata completed
- Result: Metrics, run JSON, and leaderboard entries now include a `reproducibility` object with benchmark/package/scoring versions, agent manifest path/hash, input file hashes, seed schedule hash, and seed count for rollout runs. Added concise schema documentation for the new metadata and linked it from the README.
- Evidence:
  - Changed files:
    - `src/pokerbench_ng/cli.py`
    - `src/pokerbench_ng/reporting/leaderboard.py`
    - `tests/integration/test_cli.py`
    - `docs/SCHEMAS.md`
    - `README.md`
  - Focused test pass: `.venv/bin/python -m unittest tests.integration.test_cli` ran 6 tests and passed.
  - Eval-suite pass: `.venv/bin/pokerbench-ng eval-suite --agent examples/agents/python_random_agent/agent.yaml --suite mvp_hunl`.
  - Provenance assertion passed against `reports/static_1782095498788.leaderboard.json`; `reproducibility.agent_manifest_hash` exists and scoring version was `static_v1`.
  - Full regression pass: `.venv/bin/python -m unittest discover -s tests` ran 61 tests and passed.
  - Compile pass: `.venv/bin/python -m compileall src tests`.
- Next action: Update README/docs wording to say "local-first MVP seed repo", "toy public static spot", and "smoke rollout against CallCheckBot"; avoid claiming benchmark-quality release.

### 2026-06-21 19:57 MST - item 3 explicit seat assignment completed
- Result: Rollout hands now accept explicit `agent_seat`, match runs alternate submitted-agent seats by default, each hand record includes `seat_assignment` and `net_bb_by_seat`, and submitted-agent score is computed from the assigned seat rather than implicitly from SB. Event records now include `actor_role`, and rollout reliability rates count submitted-agent decisions only when role metadata is present.
- Evidence:
  - Changed files:
    - `src/pokerbench_ng/rollout/match.py`
    - `src/pokerbench_ng/rollout/scorer.py`
    - `tests/unit/test_rollout_match.py`
    - `tests/unit/test_rollout_scorer.py`
    - `tests/integration/test_cli.py`
  - Focused test pass: `.venv/bin/python -m unittest tests.unit.test_rollout_match tests.unit.test_rollout_scorer tests.integration.test_cli` ran 17 tests and passed.
  - Rollout smoke pass: `.venv/bin/pokerbench-ng eval-rollout --agent examples/agents/python_random_agent/agent.yaml --config configs/mvp_hunl_rollout.yaml --hands 20`.
  - Smoke artifacts:
    - `reports/rollout_1782095376901.metrics.json`
    - `runs/rollout_1782095376901.json`
    - `reports/rollout_1782095376901.md`
    - `reports/rollout_1782095376901.leaderboard.json`
  - Direct artifact assertion passed: first six submitted-agent seats were `['SB', 'BB', 'SB', 'BB', 'SB', 'BB']`; run had 20 hands and 65 submitted-agent decisions.
  - Regression pass: `.venv/bin/python -m unittest discover -s tests` ran 61 tests and passed.
  - Compile pass: `.venv/bin/python -m compileall src tests`.
- Next action: Add reproducibility metadata with agent manifest/config/spot/seed hashes, scoring version, benchmark version, and package version.

### 2026-06-21 18:40 MST - item 2 reliability metrics completed
- Result: Added response classification plumbing for static evaluation and aggregate reliability rates for both static and rollout metrics. Static scoring now preserves fallback-causing classifications (`timeout`, `malformed`, `process_error`) through `EvaluatedResponse`, validates responses against spot legal actions, and counts illegal responses separately from malformed/process failures. Rollout aggregation now reports decision count plus illegal, timeout, malformed, and process-error rates from event classifications.
- Evidence:
  - Changed files:
    - `src/pokerbench_ng/cli.py`
    - `src/pokerbench_ng/static/scorer.py`
    - `src/pokerbench_ng/rollout/scorer.py`
    - `tests/unit/test_static_scorer.py`
    - `tests/unit/test_rollout_scorer.py`
  - Focused test pass: `.venv/bin/python -m unittest tests.unit.test_static_scorer tests.unit.test_rollout_scorer tests.unit.test_protocol tests.unit.test_rollout_match tests.integration.test_cli` ran 28 tests and passed.
  - Static CLI pass: `.venv/bin/pokerbench-ng eval-static --agent examples/agents/python_random_agent/agent.yaml --spots src/pokerbench_ng/data/public_spots/dev.example.jsonl`.
  - Rollout CLI pass: `.venv/bin/pokerbench-ng eval-rollout --agent examples/agents/python_random_agent/agent.yaml --config configs/mvp_hunl_rollout.yaml --hands 20`.
  - Fresh metrics evidence:
    - `reports/static_1782090805465.metrics.json` includes `illegal_action_rate`, `timeout_rate`, `malformed_rate`, and `process_error_rate`.
    - `reports/rollout_1782090807475.metrics.json` includes those reliability rates plus `decisions: 127` for 20 hands.
  - Regression pass: `.venv/bin/python -m unittest discover -s tests` ran 57 tests and passed.
  - Compile pass: `.venv/bin/python -m compileall src tests`.
- Next action: Implement item 3 by making submitted-agent seat assignment explicit in rollout hand records and alternating SB/BB over smoke rollouts.

### 2026-06-21 18:37 MST - item 1 legal-action validation completed
- Result: Implemented request-aware response validation for legal action type, numeric amounts, bet/raise min/max bounds, supplied call amount consistency, and amount-free fold/check responses. Rollout now classifies validation failures as `illegal`, uses fallback before engine application, preserves adapter classifications such as `timeout`, and has a defensive engine-rejection fallback path.
- Evidence:
  - Changed files:
    - `src/pokerbench_ng/agents/protocol.py`
    - `src/pokerbench_ng/agents/validation.py`
    - `src/pokerbench_ng/rollout/match.py`
    - `tests/unit/test_protocol.py`
    - `tests/unit/test_rollout_match.py`
  - Focused test pass: `.venv/bin/python -m unittest tests.unit.test_protocol tests.unit.test_rollout_match tests.integration.test_cli` ran 18 tests and passed.
  - CLI smoke pass: `.venv/bin/pokerbench-ng eval-rollout --agent examples/agents/python_random_agent/agent.yaml --config configs/mvp_hunl_rollout.yaml --hands 20`.
  - Smoke artifacts:
    - `reports/rollout_1782090650050.metrics.json`
    - `runs/rollout_1782090650050.json`
    - `reports/rollout_1782090650050.md`
    - `reports/rollout_1782090650050.leaderboard.json`
  - Regression pass: `.venv/bin/python -m unittest discover -s tests` ran 54 tests and passed.
  - Compile pass: `.venv/bin/python -m compileall src tests`.
- Next action: Implement item 2 by carrying response classifications into static/rollout summary metrics instead of only recording action-level fallback outcomes.

### 2026-06-21 18:35 MST - hardening loop initialized from ChatGPT review
- Result: Resumed Goalcraft Persist after ChatGPT Consultant reviewed the public repo and identified no blocker for "local-first MVP seed repo" but flagged shallow action validation as the top correctness risk before stronger benchmark-quality claims.
- Evidence:
  - Consultant thread: `https://chatgpt.com/c/6a383a82-c998-832f-9ee4-5e6a5db3930f`
  - Public repo: `https://github.com/bmendonca3/pokerbench-ng`
  - Initial pushed commit: `5763e2e4f6a0b9013aa0f4b1580b3d1599ab65ba`
- Next action: Implement item 1 in `src/pokerbench_ng/agents/validation.py`, `src/pokerbench_ng/rollout/match.py`, and focused tests.

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
