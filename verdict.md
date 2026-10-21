Fix review: blocked bf10abe62926bc8d93be779ae859a985e5365aa6 carry-missing: not carried to R10-ORCH-MACHINERY

Round 2. Head measured: bf10abe62926bc8d93be779ae859a985e5365aa6. Its tree equals the authored code head b07e9e9d8 (`git diff b07e9e9d8 bf10abe6` is empty), and origin/main is still 57f0c9c77. At writing, `git ls-remote` shows the PR head unchanged (ev/head_reread.txt). The contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Blocking

- fix-review.md step 10 and finding-propagation.md "Enforcement" are not met. Both `## Forward-carry` bullets route to R10-ORCH-MACHINERY: (1) the beat, the sweep, `record_row.py`, `ci-watch.sh` and `proof_watch.py` read `merge_train.classify`, so no third red rule is written; (2) the pre-dispatch check is `merge_train.py classify <head>`, which must exit 0 or 3. Each narrows what that not-started stage may do, and neither has been written into that stage's brief. The body names no `handoff/audit-r10-roster` SHA. At origin/handoff/audit-r10-roster 23ef06dc6, R10-ORCH-MACHINERY's `brief` and its 10 `carry` entries contain neither `merge_train.classify` nor `merge_train.py classify` (`git grep` over `dev/programme/` on the roster branch and on the pack branch 30c57744a returns nothing). The "seam with R10-ORCH-MACHINERY" line sits only in this group's own pack spec, which the ORCH-MACHINERY seat does not read. Repair, with no code change: carry both bullets to R10-ORCH-MACHINERY on the roster branch with `roster_edit.py`, each stating its control as a precondition (the e7c66485 replay with `--pending` against none, and the `classify` exit codes). Then read the write back (`brief_lint.mjs`) and name the roster SHA in the body. Carry: dismissed: blocks this PR, fixer repairs body and roster (item 3c1e0a71)

## Round-1 blocking item: repaired, with my own harness

- K15 (c) under the claimnotes driver is fixed. I built my own harness, disclosed here and kept in ev/repro.py; it is not the fixer's. It uses a clone of 57f0c9c77 with `merge.claimnotes.driver` configured as `claim-files.md` says, on real branches: a claim-note-only conflict, and a content (`roster_edit.py`) plus claim conflict. It runs a stdout+stderr runner, the `Tick.git` shape. At the round-1 head 957df90af it still gives `conflicts(m,claims) -> None` and lists `MERGE-CLAIM: resolved ...` as a file. At bf10abe6 it gives `['tests/golden/claimed_drift.txt']` with the claimnotes repair, and the content case gives `[claim, roster_edit.py]` with "back to the owning fixer". The clean case is `[]` and an unknown head is `None`. Null control in the same clone: bare `git merge-tree` exits 0, prints `MERGE-CLAIM: resolved`, and the driver runs (ev/conflicts_with_driver.txt). Carry: dismissed: confirmed repaired, nothing owed (item 5b7d2e90)
- Body null control re-run: with merge_train-12 applied by hand at the head, `orchestrator_tick.py --self-test` fails exactly 3 checks (186 total), the two real-git DIRTY arms. My harness reproduces both round-1 shapes under the same mutant (ev/null_control_tick_mt12.txt). Carry: dismissed: confirmed claim, nothing owed (item 6a4f1c2b)

## RESULT lines

- RESULT self-tests: under python3.11 the base 57f0c9c77 gives 198/168/14 checks and the head gives 219/186/16, all with 0 failed (ev/selftests.txt). These equal the body. Carry: dismissed: confirmed claim, nothing owed (item 7d3e9b14)
- RESULT fixer's mutants: M0 gives `0 seat step(s) red`. All 23 named ids are KILLED, each with the failed count the body quotes, and `RESULT survivors=0` (ev/mutants_fixer.txt). Carry: dismissed: confirmed claim, nothing owed (item 8e5f0a26)
- RESULT reviewer mutants at the head (ev/mutants_reviewer.txt, ev/rmut.py):
  - RV1, `build()` drops the `text_merge` drivers: KILLED, 1 failed.
  - RV2, the replacement driver is `true`: KILLED, merge_train 2 and tick 2 failed.
  - RV3, the config regex matches nothing: KILLED, 2 and 3 failed.
  - RV5, the unreadable `--overlap` line is removed: KILLED, 1 failed.
  - RV6, rc 1 of `git config` is read as unreadable: KILLED, crash plus 3 failed.
  - RV4, dropping `code not in (0, 1)` in `conflicts`: survives. It is equivalent in practice, because `is_sha(lines[0])` already refuses a fatal exit's output, and the line is unchanged since round 1.

  Round 1's survivors R1, R2, R3 and R4 are now merge_train-14, orchestrator_tick-4, merge_train-15 and merge_train-16, and each is KILLED. Carry: dismissed: survivor equivalent, nothing owed (item 9a1c4e37)
- RESULT finding replay at both ends: the e7c66485 replay (`r10_main_gate_replay.py`, sha1 266e441f) was run against a `git archive origin/main` export and against the head. With no `--pending`, both print only `END`. With `--pending mutation typing closures`, the base prints "is not green ... revert it first" and the head prints "is still running ...: a wait, not red" (ev/replay_e7c66485.txt). The body quotes match. Carry: dismissed: confirmed claim, nothing owed (item ab2d5f48)
- RESULT cheap checks at the head (ev/cheap_checks.txt): all of the following equal the body.
  - `STRUCTURE RATCHET PASSED`.
  - throwaway_git 0 refused, selftest_wiring 38/38, tmp_paths 0 refused, ref_privacy 0 refused.
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, run = `tests/entities.py`, and `ALL 2382 ENTITY CHECKS PASSED`.
  - `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `Architecture score: dS +0.0000 NULL`.

  Carry: dismissed: confirmed claim, nothing owed (item bc3e6a59)

## Other checks

- Merge: `git merge-tree --write-tree origin/main bf10abe6` exits 0 with tree f11fc6684 (ev/merge_tree.txt). VERSION, the manifest, RELEASE_NOTES, both claim files and every `*_budgets.json` are untouched (ev/untouched.txt). The only instrument move is `tests/closures.json` gaining the new harness, which is classification a new file requires. Carry: dismissed: confirmed claim, nothing owed (item cd4f7b6a)
- Red checks, from the check-runs API at the head (ev/ci_head.txt): the only red is nightly-status. It reads the last scheduled `tests.yml` run, 39563978649 on c77f89dc6, where `slow` failed at step 8 and `mutation-nightly` at step 6, as the body says, and it runs a base-restored script. The diff touches neither `tests.yml`, `tests/nightly_status.py`, nor the package, so the red is not this PR's, and the body answers it. `closures` and `Analyze (python)` were still in progress when I read them. Carry: dismissed: grades main, not this PR (item de5a8c7b)
- Spec: the group file is byte-identical at the body's pin ff1beba2a and at the brief's pin 30c57744a (only STUDY.md differs between them). Items (a) to (d) and the carries (a) to (d) are met: the new mutants are per-file ids in their instrument's block, both real-git arms use `throwaway_git_init`, the diff adds no push site (ref_privacy 0 refused), and `## Red checks` answers nightly-status. Carry: dismissed: confirmed claim, nothing owed (item ef6b9d8c)
- Class rules re-run (ev/class_rules.txt): rule 1's 22 hits are all dispositioned. Rule 2 also returns three files the body does not name, each a text hit and not a merge site (ev/class_rule2_undispositioned.txt): `orchestrator_tick.py` (message strings, and its stubbed self-test, because the tick reaches git only through `mt.conflicts`, closed here); `tools/pr/preflight.sh:173` (a comment); and `tools/policy/fixtures/wave-1b-931dffe.json` (a prose note). `merge_main_bot.merge_tree(text_only=...)` was read, and it does replace the named drivers, as the body says. No seam is open. Carry: dismissed: text hits, no open seam (item f07cac9d)
- Harness provenance: K15 commits no finder harness; its control is the e7c66485 shape in prose. `r10_main_gate_replay.py` is the fixer's own instrument, committed in this PR as 90a0a68f3, so it is not the finder's, although the body's Null control calls it "Finder's harness". I re-ran it at both ends, as above, and checked (c) with my own harness. Round 1 used its own live replay. The label should read as the fixer's own when the body is next edited for the carry. Carry: dismissed: labelling only, fix with carry (item 01b8d2e3)

bus-nonce: 954bb4c2dddb4ba467f3570a4cc38f13
