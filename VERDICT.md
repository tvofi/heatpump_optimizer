Fix review: merge 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7

bus-nonce: 7d5b5cf9f0c4e3ad3cc5653d4c266866

## Evidence

- Round: fifth review of this PR, a later round over the same reviewed head 454d4fc425 (packet `## Review scope: delta`). `git diff 454d4fc425 454d4fc425` is empty, so there is no code delta and nothing to widen to. The code findings of round 3 stand (none); its mutation proof and harness results carry over unchanged, because the branch's own diff is unchanged.
- Previous finding resolved: the round-4 block was `pr-contract` red on code-scanning alerts 57 and 58 missing from `## Red checks`. The live body (updated 2026-11-18T02:58:58Z) now names both as inherited from main at `tools/audit/seat/postmerge.py:130` and `tools/audit/seat/roster_lib.py:1158`. Re-derived on origin/main 99a4010e47: both lines are the `os.open(..., 0o644)` calls. The three-dot diff 1da13aafb7...454d4fc425 touches neither file and adds no `chmod` or octal-mode line (ev/alert-attribution.txt). The body's attribution holds.
- Live CI: `merge_train.py classify 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 --pr 3662` exits 0 at 03:14:08 UTC with `GREEN 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 pending: none red: none` (ev/classify-poll.log). That includes `pr-contract / pr-contract` and `gate`, both in the `owed-reds` set (ev/owed-reds.txt).
- Red checks: the earlier reds in the `owed-reds` set (`pr-contract / pr-contract`, `gate`, `budget-raise-gate`, `tests / mutation`, `governance / policy-docs`, `governance / env-matrix`, `governance / instrument-self-tests`) are each answered in the body. I checked that each trigger has an answer; I did not judge the answers.
- `git merge-tree --write-tree origin/main 454d4fc425` exits 0 against origin/main 99a4010e47 (ev/merge-tree.txt). No conflict.
- Three-dot 1da13aafb7...454d4fc425 leaves VERSION, the manifest version and RELEASE_NOTES.md untouched (ev/version-check.txt).
- `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Head re-read at the verdict: `refs/pull/3662/head` is 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 (ev/pr-head.txt, ev/HEAD.txt).
- Not re-derived: the alert numbers 57 and 58 against their locations, because this seat has no code-scanning API. The locations come from the body; I confirmed them against main's source lines. I ran no mutants this round, because there is no delta.
- Return-ref push: the brief's parentless commit was refused as non-fast-forward, because `probe/rev-3662-7d5b5cf9` already held round 4's verdict d23bc3a11e under this nonce. I did not force it. This verdict is a fast-forward child of d23bc3a11e, and its tree holds only this round's files (ev/push-refusal.txt).
