# Schemas

PokerBench-NG artifacts use plain JSON-compatible structures with
`schema_version: "1.0"`. The current seed repo includes committed schema files
for the artifacts emitted by the CLI:

- `schemas/metrics.schema.json`
- `schemas/run_record.schema.json`
- `schemas/leaderboard.schema.json`

Tests validate emitted artifacts with the dependency-free subset validator in
`src/pokerbench_ng/reporting/schema_validation.py`.

## Reproducibility Metadata

Generated metrics, run JSON, and leaderboard entries include a
`reproducibility` object:

```json
{
  "benchmark_version": "0.1.0",
  "package_version": "0.1.0",
  "scoring_version": "rollout_v1",
  "agent_manifest_path": "examples/agents/python_random_agent/agent.yaml",
  "agent_manifest_hash": "sha256:...",
  "inputs": {
    "config": {
      "path": "configs/mvp_hunl_rollout.yaml",
      "sha256": "sha256:..."
    },
    "seed_manifest": {
      "path": "src/pokerbench_ng/data/public_seed_manifests/hunl_100bb_mvp.example.json",
      "sha256": "sha256:..."
    }
  },
  "seed_schedule_hash": "sha256:...",
  "seed_count": 20
}
```

Static evaluation uses `scoring_version: "static_v1"` and includes a `spots`
input hash. Rollout evaluation uses `scoring_version: "rollout_v1"` and includes
the rollout config hash, seed manifest hash when present, and seed schedule
hash.

Hashes are SHA-256 content hashes prefixed with `sha256:`. Paths are recorded as
the user supplied them to the CLI or as referenced by the rollout config.
