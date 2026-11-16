Fix review: blocked 3868879d094dcebd146ddd49e7b5b551b7a7618e caused-by-overbroad: rca_lists admits any record that mentions a group, so a process RCA that lists defect groups only as dispatch-status rows is accepted as their root-cause record

bus-nonce: ca319a630aa24823a8f2825508669c7f

Round 2, a delta review over the reviewed head 95da81dcf729e71bcb6d105fe82caa24a8352a1d (the packet's `## Review scope: delta`). The delta is instrument and test only (`tools/audit/seat/`, `tools/ci/selftest_closures.json`, the delivery row); no `custom_components/` path, so nothing widens.

## Block

The previous block (`caused-by-unwritable`) is resolved in mechanism: `roster_lib.rca_lists` admits `caused_by` on a group with no `rca` of its own, and `roster_edit`'s new check writes `caused_by` on such a group, `R9-ESC`, then shows `injected` and `refix` turn from `unread` to values. But the predicate that does it is wider than the invariant it guards. The docstring says a record that names the group is one where "the group is the defect it analyses", and the body says "a record under `dev/audit/rca/` naming the group is that seat's record". The code only checks that the group's name appears somewhere in the file as a whole token.

On the real record this admits records that do not analyse the defect. `dev/audit/rca/R10-RCA-TICK-BLIND.md` is a process RCA about why the tick board did not prevent dispatch stalls. It names `R10-COMBI-TANK`, `R10-GENERIC-HEAT-CURVE`, `R10-GENERIC-HEAT-CURVE-PERSISTENT` and `R10-HOTFIX-COP-UNMEASURED` only as dispatch-status table rows and board lines. At this head, `convergence_why("caused_by", {"cause": "original", "rca": "R10-RCA-TICK-BLIND"}, <R10-COMBI-TANK>, names)` returns `None`, and so does the same call for `R10-GENERIC-HEAT-CURVE` (`ev/overbroad.txt`). So `set-field` accepts a cause for those defects that rests on a record never written about them. `injected` then prints a value where 0018's rule ("the cause recorded by the root-cause seat") says it should print NO-READ. This breaks the property the first review credited the ledger with: it prints `unread`, never a wrong value.

Scale (`ev/admissions.txt`): of the 5 round-10 escapes that the body's figure counts as admitted (`round 10 48 5 0`), 3 are admitted only through `R10-RCA-TICK-BLIND`'s status rows: `R10-COMBI-TANK`, `R10-GENERIC-HEAT-CURVE` and `R10-GENERIC-HEAT-CURVE-PERSISTENT`. Only 2 are admitted by a record that says it is the root-cause seat for that group: `R10-HOTFIX-COP-UNMEASURED` by `R10-RCA-COP-UNMEASURED`, and `R10-HOTFIX-FLOW-SETPOINT-STUCK` by `R10-RCA-SETPOINT-LATCH-DEADLOCK`. The body's `5` and `27` therefore overstate where `caused_by` can honestly be written.

The self-test does not reach this domain. Its planted record `R10-RCA-NAMED` ("Cause of R10-D, found again in R10-E-2.") admits both groups it mentions, and no case plants a record that mentions a group without analysing it.

The fixer chooses the repair. Options include:
- a declared subject in the record, such as a front-matter line or the existing "This is the root-cause seat for <group>" sentence, made a parsed field, and admit only the groups it lists;
- requiring the `cause` to be stated in the same record;
- confining the token match to a heading or subject block.

Whichever is chosen, it needs a self-test case where a record mentions a group (for example in a status table) without being its root-cause record, refused. The body's admission figures then need to be re-derived under the new rule.

## Findings

- Surviving mutant, equivalent: `loop_ledger.entered`'s `out[m.group(1)] = t` reverted to `out.setdefault(m.group(1), t)` survives. This is equivalent on today's record, where each roster file holds a group's `"group":` line once (the body's per-file counts). No case is owed. Carry: dismissed: equivalent on a file that holds each group line once, as the body measures
- Note: figure: the body's `round 11 17 3 0` (groups owing `caused_by`) reads `round 11 18 3 0` at review time. The reader ref `origin/handoff/audit-r10-roster` is live, and roster_lib warns that origin/main carries roster changes it has not merged (`ev/figures.txt`). The escape rows (`round 9 0 0 0`, `round 10 48 5 0`, `round 11 12 0 0`) and the other owing rows re-derive exactly. Carry: R11-PRE-ROUND-METRICS

## Evidence

- Previous verdict's findings at this head (`ev/mutants-ll.txt`, `ev/mutants-rl.txt`; reviewer-built driver `ev/mut.py`, one exact-string swap per mutant, the owning self-test run, the file restored):
  - These are now killed: `blame-precedence` (`FAIL history: each group's week is its first roster entry, carried into a later roster or not`), `kids-every`, `refix-recorded`, `week-unentered` and `rca-file`.
  - `blame-setdefault` survives as above.
  - The `figure` note on "every round prints unread" is resolved: the body now states round 9's and week 2026-W43's values.
  - The `stale-body` note on the repeated recarry paragraph is resolved.
- Mutants over the delta's `rca_lists` / `convergence_why`, all killed:
  - `rca-id-regex`
  - `rca-own-arm`
  - `rca-name-arm`
  - `rca-substring` (`me in text`)
  - `rca-nostrip`
  - `rca-bool-own`
  - `cw-rca-gate` (the gate replaced by `if False`)
- Self-tests at the head (`ev/selftests.txt`). These match the body's figures:
  - `loop_ledger self-test: 0 failed`
  - `roster_lib self-test: 97 checks, 0 failed`
  - `roster_edit self-test: 315 checks, 0 failed`
  - `throwaway_git: 0 raw git init or clone site(s) refused`
- Merge: `git merge-tree --write-tree origin/main 3868879d...` exits 0, printing `LEDGER-MERGE: resolved tests/closures.json`. No conflict.
- Role contract: `git diff <mb>...origin/main -- dev/governance/roles/` touches `COMMON.md`, `architect-planner.md` and `orchestrator.md`. `fix-review.md` is current.
- Version: no `VERSION`, manifest or `RELEASE_NOTES.md` path is in the three-dot diff.
- Head: `refs/pull/3657/head` reads 3868879d094dcebd146ddd49e7b5b551b7a7618e at the verdict (`ev/HEAD.txt`).
- CI: `merge_train.py classify 3868879d... --pr 3657` printed `WAIT 3868879d094dcebd146ddd49e7b5b551b7a7618e pending: gate red: none` on every poll from 10:08Z to 10:12Z (`ev/classify.txt`). The poll was stopped because the block is on code and does not depend on CI. The only red in the packet digest, `tests / nightly-status`, is not in `owed-reds`, so no `## Red checks` answer is owed. The packet's `introduced-red: unreadable` refusal came from `instrument-self-tests` still being `in_progress` when the packet was rendered.
- Finder's harness: none is named. This is an instrument build. The instruments used here (`mut.py` and the `admissions` and `overbroad` probes) are the reviewer's.
- Figures not re-derived: `Architecture score: dS +0.0000 NULL`, `STRUCTURE RATCHET PASSED` and the `selftest_scope record` line are cited from the body and CI, not re-run.
