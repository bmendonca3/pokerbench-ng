# Data and Leakage Policy

## Public Data

Public dev data may include spot inputs, legal actions, tags, toy labels, baseline reports, and generation scripts.

The current `dev.example.jsonl` suite is hand-authored toy coverage for evaluator plumbing and regression tests; it is not solver-grade benchmark data.

## Hidden Data

Hidden leaderboard data must not expose active hidden spot text, hidden solver EVs, hidden seed manifests, or per-hidden-spot feedback.

## Clean-Room Policy

Do not copy source code from source-available or license-restricted benchmark repositories. Feature-level inspiration and independently written compatible schemas are acceptable.
