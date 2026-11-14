Fix review: merge 2c4889ddbcc13c84bc352cf334452a2657d6aee5

bus-nonce: 5f62a1444edc38a46c7ccf3de2287a70
pending-ci: gate

## Summary

Round 4. This is a delta review over the reviewed head b392956a14ea5f0f59a07e3805b15eeb8b7082ec, measured at head 2c4889ddbcc13c84bc352cf334452a2657d6aee5. The packet's scope line reads `delta`.

The delta is made only of main merges:
- d27b79d5b1 merges origin/main 9fdba3b854 into b392956a14. This is the conflict repair, with two conflicts resolved by hand.
- 8fc9551189 merges d27b79d5b1. Its tree is identical to d27b79d5b1's (`git diff --stat` is empty).
- 2c4889ddbc merges origin/main 5cd7b87413 cleanly. `--remerge-diff` shows nothing.

No authored commit was added since the reviewed head.

The head's tree equals a synthetic `git merge-tree 5cd7b874 b392956a` everywhere except the two conflict hunks (ev/synth_merge.txt). So the pull request's own patch is the reviewed one plus main's side, and nothing more. The two resolutions match the body's account:
- duty_switch.py docstring: main's sentence was kept. That is docstring only, no code line.
- tests/doc_claims.py `main()`: a union of the three calls.

No production resolution puts already-reviewed code at risk, so the review does not widen. The previous verdict at b392956a14 had no findings, so nothing is outstanding.

## Findings

none

## Evidence

- Head measured: 2c4889ddbcc13c84bc352cf334452a2657d6aee5 (ev/HEAD.txt). It matches the body's `## Head` and `refs/pull/3568/head` (ev/body_checks.txt).
- Patch preservation (ev/synth_merge.txt): `git diff <merge-tree 5cd7b874 b392956a> 2c4889dd` touches only the two conflict regions.
  - duty_switch.py: main's "at a booking and on each decay, so a record stored over it is held to it by the first pass" replaces the stacked 3532 wording. The code at the head does both things the sentence describes: `Direction.book` `scale = min(1.0, N_CAP / self.n)` at line 232, and decay `min(self.weights(when)[1], N_CAP) / n` at line 202.
  - doc_claims.py: `check_late_delta_claims`, `check_flow_text_claims` and `check_docs_strings_residue` are all called. Each `def` appears once (count 3).
- Remerge (ev/remerge.txt): d27b79d5 shows exactly those two conflict hunks plus the ledger driver's `LEDGER-MERGE: resolved tests/closures.json`. 2c4889dd shows no hand edit.
- Body claim "the merged file is byte-identical to 3532's current head" holds at 3532's live head 32c768ae03. That head is not the 3ab3d5b5ab the body names, which has since moved. `git diff 32c768ae03 d27b79d5 -- duty_switch.py` and `git diff 32c768ae03 2c4889dd -- duty_switch.py` are both empty. The stacked fd5fe52fa7 is an ancestor of 32c768ae03.
- doc_claims:
  - at d27b79d5: ALL 406 checks PASSED, as the body states (ev/doc_claims_d27.txt).
  - at the head: ALL 410 checks PASSED, rc 0 (ev/doc_claims_head.txt). The extra 4 come from main 5cd7b874.
- Mutation re-run at the head, after the merge (ev/mutants.txt). Each mutant failed and was restored; afterwards `git status --short custom_components` was empty.
  - `FLOW_BIAS_CLAMP_K = 10.0`: rc 1, `FAIL docs/configuration.md bias`.
  - `leg_rule` `first = "dhw"`: rc 1, `FAIL docs/configuration.md split`.
- STRUCTURE RATCHET PASSED at the head (ev/structure.txt).
- Untouched files: VERSION, manifest.json, RELEASE_NOTES.md and both claim files show an empty three-dot diff against merge-base 5cd7b874 (ev/untouched.txt).
- Role contracts are current: `git diff mb...origin/main -- dev/governance/roles/` is 0 lines.
- Merge with main: `git merge-tree --write-tree origin/main 2c4889dd` rc 0. That held at 5cd7b874 and again at ebff4c1b5a, main's tip at 18:12 UTC.
- Ordering: 3532 (fd5fe52fa7) is still stacked and not on main. 3562 and 3556 are now on main. The body says this pull request merges only after 3532, and the train must honour that.
- Red checks: `owed-reds` is in ev/owed_reds.txt. The body's `## Red checks` answers the stacked heads' historical reds as theirs. Live state at this head is in the classify lines below.
- Packet refusal `introduced-red: unreadable` (instrument-self-tests in_progress at render): classify decides, see below.
- Not re-derived: the body's local tests/run.sh scoped line and its macOS red scripts. I cite CI for those.
- CI: `merge_train.py classify 2c4889dd --pr 3568` printed `WAIT 2c4889ddbcc13c84bc352cf334452a2657d6aee5 pending: gate red: none` on every run from 17:42 to 18:12 UTC, 30 runs (ev/classify_poll.txt). No required check reads red, so this verdict returns with `pending-ci: gate`. `refs/pull/3568/head` was still 2c4889dd at 18:12.
