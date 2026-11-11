Fix review: merge cbf80c6e8b67b016d729b22f73c343b1f3eeaaed

bus-nonce: 5c3ac780c70446475b7c8dbd7d7ccad3

## Round

Round 1 (first review, full scope). Measured at head cbf80c6e8b67b016d729b22f73c343b1f3eeaaed from detached worktrees at that SHA; merge base cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Evidence

- CI: `merge_train.py classify cbf80c6e --pr 3455` returned rc 0 `GREEN cbf80c6e8b67b016d729b22f73c343b1f3eeaaed pending: none red: none` at 12:13:52Z (ev/classify.log, ev/classify_final.txt).
- Merge: `git merge-tree --write-tree origin/main cbf80c6e` (origin/main ee64358b) rc 0, `LEDGER-MERGE: resolved tests/closures.json`, no conflict (ev/merge-tree.txt).
- Mutation proof, re-run by me, in place: `bash tools/pr/prepr.sh --self-test` at the head gives `525 passed, 0 failed`. Three hand-applied mutants of `mutants_line` (diffs in ev/mutant-m*.diff):
  - `rc_check_off` (`if [ "$r" -ne 0 ]` -> `if false`): 522 passed, 3 failed. Killed, including "a MUTANT_CMD failing on the unedited tree is refused".
  - `in_place_dropped` (`${MUTANT_IN_PLACE:+--in-place}` deleted): 524 passed, 1 failed. Killed ("the same check under MUTANT_IN_PLACE=1 ... passes").
  - `survivor_reads_ok` (`if [ "$n" -gt 0 ]` -> `if false`): 523 passed, 2 failed. Killed.
  - `flow_drops_cmd` was not re-run. The flow check `case "$flow" in *'mutants_line "$PWD" "$BASE" "${MUTANT_CMD:-}"'*` pins it by text.
  - ev/selftest-*.txt.
- Two figures differ from the body (not re-derived exactly). The body has 524 passed at the head and 2 failures under rc_check_off; here it is 525 and 3. The totals are consistent (522+3 = 525), so one check is environment-dependent: the archive-copy git-checkout case also fails under the mutant in this seat. The direction is a stronger kill, not a weaker one.
- Null controls: the self-test's own null ("a check killing every mutant ... passes") and "MUTANT_CMD unset skips" pass at the head. The harness counter's null (class `no-such-class` over the same window) gives 0 (ev/harness-rederive.txt).
- Coverage term re-derived with the harness:
  - `fetch`, then `blocks 2026-11-04T06:52:35+01:00 2026-11-11T06:52:35+01:00 mutation-vacuous` gives 36 (ev/blocks-mutation-vacuous.txt), matching the body.
  - Spot checks: 3248@c8c50b9f `ledger.py:296` rank=1 of 25 (within the cap). For 3193@af8ff29b (a `rank -> none` entry), the `--list` run exits rc 0 with 27 mutants (ev/list-3193.txt), so its listing is real and not a masked refusal.
  - I did not re-run the 36 per-block `run` reproductions or the 10-diff wall times (1632 s). The 5/36 reproduced count is the fixer's.
  - The refusal of (b) is robust: it would flip only if 13 or more of the 29 "not reproduced" were wrong.
- Repair hours re-derived: `repair 3405 38e3d17e` gives 18.66 h and `repair 3419 245ddf78` gives 15.96 h, matching the body. (a)'s saving (18.66 h, or 2.62 h of repair commits, not re-derived) against the added 0.45 h holds by a wide margin even if the wall time is several times off.
- Policy budget figures re-derived (`node tools/policy/policy_lint.mjs --budgets`): corpus ~68671 -> ~68667, `tools/audit/briefs/fixer.md` 315 -> 314 lines (cap 315), role fixer ~6265 flat (ev/policy-budgets-*.txt).
  - The cuts are restatements. "Compare three-dot" stays in CLAUDE.md rule 3. The owed-reds naming stays in `defect-root-cause.md`'s Enforcement ("Only a red on a required check is owed an answer ... `merge_train.py owed-reds`"), which loads with fixer.md through `dev/governance/**`.
  - The metric movement is earned by deleted text (step 14).
- fixer.md's new sentence checked against `tools/audit/seat/mutant_run.py`:
  - `--diff` mutates only `*.py` (`git diff ... -- "*.py"`) and skips `SKIP_PREFIXES = ("tests/", "dev/")`.
  - `--max-mutants` keeps the first N in file order.
  - BASELINE FAILS and a killed NULL are rc 3 and a refusal is rc 2, which are exactly the cases `mutants_line` now refuses.
  - The sentence's domain claim is accurate.
- Class (step 6): every tracked caller of `mutant_run.py` that gates on its result was enumerated.
  - The only gating callers are `prepr.sh`'s `mutants_line` (this fix) and `governance.yml`'s self-test step, which pipes into a `0 failed` grep under pipefail.
  - The class is closed in this diff. The two non-gating readers are under Findings.
- Carries checked against the roster at `handoff/audit-r10-roster` 352b9cda, group R10-FIXER-MD-SPELLING-CORPUS carries 0-6 (body ordinals 1-7):
  - 0 and 1 (measure-first and coverage term) are measured, with (a) landed and (b) refused, both numbers stated.
  - 3 and 4 are `[dismissed: duplicate ...]`.
  - 5 is discharged by this measurement.
  - 2 and 6 are `[moved: R10-ROUND-PLAYBOOK-FINAL]`.
  - The body's one forward-carry is dismissed as landed in fixer.md step 2's own sentence, which states the 40-mutant `.py`-only domain. Confirmed in the diff.
- Harness (step 9): the measure-first had no committed finder's harness. `dev/audit/harnesses/r10_mutant_coverage.sh` is the fixer's, is disclosed as built by this PR, and lands in the tree (closure entry added in `tests/closures.json`).
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched (the diff's 6 files are named in the packet). No golden fixture or claim file is in the diff, so `env_drift.py` has nothing to compare.
- Head (step 7): the body names cbf80c6e as its head. Its second SHA, ecf3c51c, is the prepr worktree it measured from a7628041. `tools/pr/prepr.sh` is the file under proof, and I measured it at cbf80c6e directly.
- Unpinned sites: the diff adds no `.py` production line, so `none` is correct.
- Policy: fixer.md is policy. The roster's `owner_gate` is `policy: merges under mandate 6624093439`, and the body requests the owner's review. That gate is the merge seat's, not this verdict's.

## Red checks

- `gate` (in the owed-reds set) concluded failure twice at this head: 11:02:47Z (id 130481537662) and 11:05:56Z (id 130483409628). Both concluded before `tests / closures` finished (11:46:44Z), which is the sibling race the dispatch names.
  - `pr-contract / pr-contract` (id 130502882238) started at 11:47:53Z, after the last red concluded. It passed on this body, so under fix-review.md step 11 that green run is the evidence that the trigger was answered.
  - Later `gate` runs at this head are green: 11:50:16Z, 12:01:27Z and 12:12:44Z (ev/check-runs.tsv).
- `tests / nightly-status` is red. It is outside `merge_train.py owed-reds` (ev/owed-reds.txt): main's nightly lane, not owed here.

## Findings

- Follow-up: `dev/audit/harnesses/r10_mutant_coverage.sh` `rank` drops `mutant_run.py`'s rc, so a refused `--list` prints `rank=none`, which reads the same as "diff mode draws no mutant there". `run` echoes rc and the BASELINE line but always exits 0. This is the fail-open shape this PR removes from prepr, kept in its own measurement instrument. Spot-checked at rc 0 for 3248 and 3193, so no stated figure is shown wrong. Carry: dismissed: one-shot measurement instrument whose figures were spot-checked at rc 0; no gating caller reads it.
- Follow-up: prepr.sh's new self-test counts `--list` mutants (`nl=$(... --list | grep -c '^MUTANT lib.py:')`) without checking rc, so a failed listing would compare 0:0. A diff that `--list` cannot read would also make the `--cmd true` run in the assertion before it (`st "$r" 2`) fail, so that assertion fails first; reasoned from the code, not constructed. `survivor_reads_ok` is killed through these lines. Carry: dismissed: guarded by the preceding rc assertion on the same diff.
- Out of scope: the body says carries 3 and 7 "stay pending the orchestrator's ruling". The roster at 352b9cda records both as `[moved: R10-ROUND-PLAYBOOK-FINAL]` by orchestrator ruling 2026-11-11, so the wording is stale and the disposition is already made. Carry: dismissed: the roster already records the move; body wording only.

## Friction

none
