# Metrics

## Static EV-Loss

```text
best_ev = max_a EV(a)
chosen_ev = EV(normalized_agent_action_bucket)
ev_loss = best_ev - chosen_ev
```

Report raw EV loss as the primary scientific metric. Exact action agreement is diagnostic because many poker spots are mixed.

## Reliability

- illegal action rate,
- malformed response rate,
- timeout rate,
- fallback action count.

## Rollout

```text
bb_per_100 = 100 * total_net_bb / hands_played
```

Rollout metrics must include confidence intervals once the evaluator runs real hands.

