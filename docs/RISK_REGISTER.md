# Risk Register

| Risk | Severity | Mitigation |
|---|---:|---|
| Tournament results are noisy | High | Static EV-loss primary; rollout CIs mandatory; arena secondary. |
| Solver labels are brittle | High | Use EV loss, convergence metadata, and human review samples. |
| Hidden set leakage | High | Aggregate-only hosted feedback, canaries, rotation, rate limits. |
| License contamination | High | Clean-room implementation and dependency review. |
| Engine bug invalidates results | High | Property tests, golden histories, independent validation. |

