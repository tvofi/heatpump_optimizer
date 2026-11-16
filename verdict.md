Fix review: merge c0d7066c07d488c95763fa56db8c18a7517b3abe

bus-nonce: ebc208825d8cc5ec3d76534f09faaa7b
pending-ci: gate

Round 3. This is a delta review over the reviewed head 3868879d094dcebd146ddd49e7b5b551b7a7618e (the packet's `## Review scope: delta`). The delta is one commit, c1a69f7a02 (`rca_lists: admit only a group a record declares its subject`), plus the merge c0d7066c07 that brings it onto the branch. `git diff --stat c1a69f7a02 c0d7066c07` is empty. The delta touches `tools/audit/seat/roster_lib.py`, `roster_edit.py` and `instruments/loop_ledger.py.md`. No `custom_components/` path is touched, so nothing widens.

## Findings

- Surviving mutants, equivalent on today's record. Four of the reviewer's mutants of `roster_lib.rca_subjects` survive `roster_lib.py --self-test`:
  - `split-strict`: the paragraph split `\n[ \t]*\n` becomes `\n\n`.
  - `table-nolstrip`: the table-row filter stops calling `lstrip()`, so indented table rows are no longer dropped.
  - `no-strip-text`: the `text.strip()` before the split is dropped.
  - `no-pstrip-filter`: empty paragraphs are filtered by `if p` instead of `if p.strip()`.

  Each one changes the result only for a record with whitespace-only separator lines, an indented table, or leading blank lines. None of the 128 records under `dev/audit/rca/` has that shape: each mutant's subject set equals production's on every record (`ev/survivor_corpus.txt`). A case for each is cheap but not owed by this repair. Carry: dismissed: equivalent on every record under dev/audit/rca/ at the head (ev/survivor_corpus.txt); the mechanism under review, opening block against status row, is killed by the seven mutants in Evidence
- Note: figure: the body's round-11 rows `round 11 12 0 0` (escapes) and `round 11 18 0 0` (groups owing `caused_by`) read `round 11 13 0 0` and `round 11 19 0 0` at review time. The reader ref `origin/handoff/audit-r10-roster` moved from the body's `c9d838fdfc` to `5e4fdcb7cd` (`ev/figures.txt`). Round 9 and round 10 re-derive exactly: `round 10 48 2 0`, `round 10 123 16 5` and `round 9 14 1 0`. Carry: R11-PRE-ROUND-METRICS

## Evidence

- Previous verdict's block (`caused-by-overbroad`): resolved.
  - `rca_lists` now admits a group with no `rca` of its own only when the group is in `rca_subjects(text)`. That set is the record's opening paragraph, plus the next paragraph when the first is a one-line `# ` title, with table rows dropped.
  - `R10-RCA-TICK-BLIND`'s opening block names no group, only its own id (`ev/subjects.txt`). So `R10-COMBI-TANK`, `R10-GENERIC-HEAT-CURVE` and `R10-GENERIC-HEAT-CURVE-PERSISTENT` are no longer admitted.
  - The round-10 escapes admitted at the head are exactly `R10-HOTFIX-COP-UNMEASURED` and `R10-HOTFIX-FLOW-SETPOINT-STUCK` (`ev/figures.txt`).
  - Every group that owes `caused_by` and is admitted through the subject arm is admitted by a record whose opening declares itself that group's root-cause seat (`ev/owing-admitted.txt`). I read the openings of `R10-RCA-MAIN-SELFTESTS-RED`, `r10-gate-busy-defer-2` and `R9-RCA-1736`.
  - The self-tests now plant a status-row record: `R10-RCA-STATUS` in `roster_lib`, `R10-RCA-BOARD` in `roster_edit`. Both are refused.
- Previous verdict's findings:
  - The `blame-setdefault` survivor is dismissed as equivalent. The body now removes it from the pinned list.
  - The round-11 figure note is restated above at the moved ref.
- Mutation proof over the delta (reviewer's driver `ev/mut.py`: one exact-string swap per mutant, `roster_lib.py --self-test` run, file restored; `ev/mutants.txt`). Each of these fails `convergence: caused_by admits only a group the record declares its subject, never a status row`:
  - `whole-text` (the blocked head's rule restored)
  - `all-paras`
  - `always-two`
  - `no-table-filter`
  - `title-multiline`
  - `title-hash`
  - `title-never`
  - `tok-nostrip`
  - Four further mutants survive, as listed under Findings.
- Self-tests at the head (`ev/selftests.txt`). These match the body:
  - `roster_lib self-test: 98 checks, 0 failed`
  - `roster_edit self-test: 315 checks, 0 failed`
  - `loop_ledger self-test: 0 failed`
  - `throwaway_git: 0 raw git init or clone site(s) refused`
- Body figures re-derived at the head (`ev/figures.txt`):
  - `seat-for 32 of 128` (the "root-cause seat for" regex).
  - `R10-RCA-TICK-BLIND` has 31 lines naming a `#<n>`.
  - No record opens with `---` on its first line.
- Merge: `git merge-tree --write-tree origin/main c0d7066c07` exits 0, printing `LEDGER-MERGE: resolved tests/closures.json`. No conflict.
- Role contract: `git diff <mb>...origin/main -- dev/governance/roles/` touches `COMMON.md`, `architect-planner.md` and `orchestrator.md`. `fix-review.md` is current.
- Version: no `VERSION`, manifest or `RELEASE_NOTES.md` path is in the three-dot diff.
- Finder's harness: none is named. This is an instrument build. The instruments used here (`mut.py`, `survivor_corpus.py` and the figure probes) are the reviewer's.
- Figures not re-derived: `Architecture score: dS +0.0000 NULL`, `STRUCTURE RATCHET PASSED` and the `selftest_scope record` line are cited from the body and CI.
- Head: `refs/pull/3657/head` reads c0d7066c07d488c95763fa56db8c18a7517b3abe at the verdict (`ev/head-at-verdict.txt`, `ev/HEAD.txt`).
- CI: `merge_train.py classify c0d7066c07... --pr 3657` printed `WAIT c0d7066c07d488c95763fa56db8c18a7517b3abe pending: gate red: none` on every poll from 14:32Z to 15:02Z and on a final run after that (`ev/classify.txt`). Following the brief, the verdict is returned with `pending-ci: gate`.
  - The live check runs show one completed red, `tests / nightly-status`. It is not in the set `merge_train.py owed-reds` prints, so no `## Red checks` answer is owed.
  - The `gate` aggregate reads `failure` in the check-run list, but classify reads it as pending with no red. Classify decides.
  - The packet's `introduced-red: unreadable` refusal came from `instrument-self-tests` still being `in_progress` when the packet was rendered.
- Self-audit: `carry_audit.py check` over the PR body and this verdict exits 0 (`CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`).
