# Playbook fixture (null control)

brief_lint.mjs's playbook arm must lint this file clean: every backticked
path resolves in the tree, as a directory, or at the cited commit d5d8c4a.

| phase | instrument | contract |
|---|---|---|
| stamps | `tools/release/stamp.py --push --push-key` | `dev/governance/roles/orchestrator.md` |
| beat | `tools/audit/seat/beat_jobs.py` | `dev/governance/roles/standing-tick.md` |
| seats | `tools/audit/seat/` | `fixer.md` |
| archive | `tools/audit/round2/JUDGE.md` at d5d8c4a | -- |

Not a citation: `mock.patch.object`, `--budgets`, `MODE: FULL`.

```
tools/audit/seat/inside_a_fence_is_skipped.py
```

    tools/audit/seat/indented_is_skipped.py
