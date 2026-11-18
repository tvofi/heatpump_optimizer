Fix review: blocked 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 red-check: pr-contract red at this head on code-scanning alerts 57 and 58 missing from the body's Red checks (body-only; code delta clean, no code finding)

bus-nonce: 7d5b5cf9f0c4e3ad3cc5653d4c266866

## Block

`merge_train.py classify 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 --pr 3662` exits 1 at 02:15:41 UTC: `RED 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 pending: none red: gate` (ev/classify-poll.log). Both `gate` jobs fail only on `FAIL pr-contract / pr-contract`: job 134520105095 in run 44219013946, and job 134519357204 in run 44219577902. The `pr-contract` job 134518677096 in run 44219577902 has two errors, both from `[pr-body]`: check `code-scanning alert 57 (py/overly-permissive-file)` is red and `## Red checks` does not name it; the same holds for alert 58 (ev/pr-contract-run-44219577902.txt). This round's body repair fixed the previous block: `figure_block verify` reports 1 block, 0 refused, and carry_audit reports 10 routed, 0 unrouted. The two alerts are a new red, introduced after the previous round. This is paperwork (C5), which would be a Note under `merge`, but a red head takes no `merge` (C8). The repair is body-only: add both alerts to `## Red checks` with their answer, and pr-contract re-runs on the edit.

## Red checks

- `pr-contract / pr-contract` and `gate` are in the `merge_train.py owed-reds` set. Cause: code-scanning alerts 57 and 58 (`py/overly-permissive-file`), which `codescan_wait.py --pr 3662 --base main` returns, are not answered in the body. The branch's three-dot diff from 1da13aafb7 adds no `chmod` or `0o7xx`/`0o666`/`0o777` line. The Python files the branch touches are accuracy.py, coordinator.py, store.py, two cop harnesses and tests/features.py (ev/alert-attribution.txt). So the alerts' code is most likely not this PR's own. That is a fact for the author's answer, not a figure I re-derived: I did not read the alerts' locations, because this seat has no code-scanning API read. The cheaper detector is the body's `## Red checks` check against `codescan_wait.py`, which `prepr.sh` runs before a body push. Classified root-cause-detectable.
- `tests / nightly-status` and `tests / replay` are red (run 44194991877) but not in `owed-reds`. They are neither answered nor a block.

## Evidence

- Round: this is the fourth review of this PR, a delta over 9894911a81, whose verdict was `blocked red-check`. From the fourth round on, `fixer.md` owes a re-cut. All three earlier blocks after round 1 were body or CI paperwork, not code.
- Delta: `git log --first-parent 9894911a81..454d4fc425` is one commit, 454d4fc425 `ci: merge main` (parents 9894911a81, 1da13aafb7). Its `git show --remerge-diff` is empty. The driver resolved `tests/structure_budgets.json` (class_excess_loc 17385 + both deltas = 17382) and `tests/closures.json` (merged as a set) (ev/remerge-diff.txt). `review_carry.py 9894911a81 454d4fc425` prints `CARRY`: 0 of 1 branch-only commits are non-merge (ev/review_carry.txt). The earlier verdict was a block, though, so nothing carries, and this delta review stands in its place.
- Production delta: everything in `git diff 9894911a81 454d4fc425 -- custom_components` comes from main's side. Files: const.py, ledger.py, mixing_valve.py, narrative.py, optimizer.py, strings.json, thermal_model.py, translations, the card (ev/prod-delta-stat.txt). None of it touches accuracy.py (ScaleDither, ScaleProbe) or `coordinator._fold_measured_cop`, which the earlier rounds reviewed. The merge resolution is empty, so there is no non-obvious risk to widen to. Not widened.
- Previous finding resolved. `figure_block verify` reports `1 block(s), 0 refused` at this head in CI, and the body's scope-line block names mb=1da13aafb7 head=454d4fc425. The code findings of round 3 stand (none). Its mutation proof and harness results (probe/rev-3662-* at 9894911a81) carry over unchanged, because the branch's own diff is unchanged.
- `git merge-tree --write-tree origin/main 454d4fc425` exits 0 against origin/main 99a4010e47 and prints `LEDGER-MERGE: resolved tests/closures.json`. No conflict (ev/merge-tree.txt).
- Three-dot `1da13aafb7...454d4fc425` leaves VERSION, the manifest version and RELEASE_NOTES.md untouched. CI's prepr `--version-edit` agrees.
- `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Head re-read at the verdict: `refs/pull/3662/head` is 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 (ev/HEAD.txt).
- Not re-derived: the source location of alerts 57 and 58, because there is no code-scanning read from this seat. I ran no mutants this round, because the delta has no branch code.
