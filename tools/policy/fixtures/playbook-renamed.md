# Playbook fixture (renamed and removed instruments)

brief_lint.mjs's playbook arm must refuse this file four times (the fourth is the stated open-PR cap in the last line): the stamp renamed, the beat job removed and the state-doc pusher moved to another directory; every other backticked
path resolves in the tree, as a directory, or at the cited commit d5d8c4a.

| phase | instrument | contract |
|---|---|---|
| stamps | `tools/release/stamp_renamed.py --push --push-key` | `dev/governance/roles/orchestrator.md` |
| beat | `tools/audit/seat/no_such_beat.py` | `dev/governance/roles/standing-tick.md` |
| seats | `tools/audit/seat/` | `fixer.md` |
| state docs | `tools/pr/state_docs.py` | `standing-tick.md` |
| archive | `tools/audit/round2/JUDGE.md` at d5d8c4a | -- |

Not a citation: `mock.patch.object`, `--budgets`, `MODE: FULL`.

```
bash `tools/audit/seat/inside_a_fence_is_skipped.py`
```

    `tools/audit/seat/indented_is_skipped.py`

The open-PR cap is 16 in round 10.
