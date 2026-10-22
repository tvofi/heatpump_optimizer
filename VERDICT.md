Fix review: merge 48e8c29b7ffe23df442d563b7ae81d81e7475d4e

bus-nonce: fe39a9af50baca9487d87c76abdfe040

## Round

Round 2 of R10-NIGHTLY-ABSENT-NEW (#2627), reviewed in a detached worktree at 48e8c29b7ffe23df442d563b7ae81d81e7475d4e. The PR head was re-read at the start and again before writing this verdict, and it was unchanged both times. The merge base is fef4a1351db3e8e328d714e84299284c6876eecb, which is also origin/main, so the head is 0 commits behind main. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.

## Findings

- A mutant survives: `SCHEDULE_LATENCY = dt.timedelta(0)` (ev/mutant_M5.diff) leaves all 2402 entity checks green. The fixtures sit at 9 h and 26 h, so nothing pins the one-hour grace between 24 h and 25 h. My probe measured the edge directly: 24.9 h reads NEW and 25.0 h reads ABSENT (ev/probe_both_ends.txt). The mutant only makes the window stricter, by one hour, and fails toward red, so a dead schedule is never hidden. Carry: dismissed: a mutant on the strict side of a bound the null control already pins on its loose side; a 24.5 h fixture would close it if a later edit touches this arm.
- A mutant survives: removing the `created_at > now` guard (`if created > now:` changed to `if False:`, ev/mutant_M6.diff) leaves all 2402 checks green. The missing-`state` `Unreadable` branch is not exercised either. Without the guard, a `created_at` ahead of the runner's clock gives a negative age and reads NEW, which is green. That needs GitHub's server stamp to be ahead of the runner's clock, and it is still bounded by the same 25 h window. The body's `## Unpinned sites` line says "every production line this diff adds is reached by the three new entities checks". That overstates coverage: the two `Unreadable` raises are not reached. Carry: dismissed: a fail-closed guard that is correct but unpinned, reachable only under clock skew between GitHub and the runner and bounded by the window; the overstated n/a line is recorded here rather than worth a round 3.
- The code comment and the body say GitHub stamps the workflow's `created_at` with `+02:00` "live". My live read of `actions/workflows/nightly.yml` returned `2026-10-22T08:05:56.000Z` (ev/nightly_workflow_record.json). I could not re-derive the `+02:00` observation. The parser handles both forms: the head's live run printed the correct 14.7 h age from the `Z` stamp. Carry: dismissed: comment-only wording, and the code is correct for both offsets.
- The delivery row `dev/programme/delivery/2627.md` repeats the group tag: `(R10-NIGHTLY-ABSENT-NEW) (R10-NIGHTLY-ABSENT-NEW)`. The roster carry's prefix also reads `From #2627 (R10-NIGHTLY-ABSENT)`, without `-NEW`. Carry: dismissed: cosmetic; the row is regenerated at merge, and the carry's text and its stage are correct.

## Evidence

- Verify 1, NEW/ABSENT against the brief's controls at both ends. No harness for this finding is committed (the brief's controls are prose), so ev/probe.py is my own instrument: it drives `verdict()` from each worktree's `tests/nightly_status.py`.
  - Merge base fef4a1351: `RESULT young-9h state=ABSENT exit=1`. This is the defect, and it also reads ABSENT at 26 h, 72 h, disabled and no-record.
  - Head: `RESULT young-9h state=NEW exit=0`, `edge-24.9h NEW 0`, `edge-25.0h ABSENT 1`, `late-26h ABSENT 1 inactivity_claim=False`, `late-72h ABSENT 1`, `disabled-9h ABSENT 1` (names 'disabled_inactivity'), `norecord-9h ABSENT 1`.
  - Both arms are exercised: a young workflow reads NEW, and a workflow past its window with no run is still ABSENT.
- The finder's live reading, both ends (ev/live_both_ends.txt). The record is `state=active`, `created_at 2026-10-22T08:05:56Z`, with 0 schedule runs at 2026-10-22T22:5xZ.
  - The base copy printed the false `GitHub disables schedules ... no recent activity`, rc 1.
  - The head copy printed `NIGHTLY NEW ... 14.7 h ago`, rc 0.
  - This matches the body's 14.4 h reading at 22:30Z.
- Mutation proof (`env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`, Python 3.14.7, one worktree per mutant). The head reads `ALL 2402 ENTITY CHECKS PASSED` rc 0. The body says 2400, measured at 43bc60d2e; main's merge into this head added 2 checks. Each mutant's `FAIL` lines were diffed against the head's.
  - M1, grace dropped: `1 of 2402 FAILED`, the NEW/ABSENT check (`26 h -> ('NEW', 0)`). Killed.
  - M2, state read dropped: `1 of 2402 FAILED`, the same check (`disabled -> ('NEW', 0)`). Killed.
  - M3, the record GET in `collect()` replaced by `None`: `1 of 2402 FAILED`, the read-count check. Killed.
  - M4, `NEW_WINDOW = 2 * SCHEDULE_PERIOD`: `1 of 2402 FAILED`. Killed.
  - M5 and M6 survive; see Findings.
  - The `a8:register_once` and `hb:positive_control` sub-case lines appear in every run, including the head's passing one, with randomised contents. This confirms the body's null control for "the one check".
- Verify 2: `git diff fef4a1351...48e8c29b7 --stat` lists only `dev/programme/delivery/2627.md`, `tests/entities.py` and `tests/nightly_status.py` (ev/diff_stat_3dot.txt). The roster is not in the diff. numstat is +109/-24 and +87/-2, matching the body.
- Verify 3: 0f690a952102eb8840d86764f1fbbf2d8d4d1bf1 exists, is an ancestor of origin/handoff/audit-r10-roster (0ae379878), and is one `roster_edit append-carry R10-CI-LAYOUT-P2` commit.
  - It appends to R10-CI-LAYOUT-P2's carries the body's forward-carry text, verbatim, including its control (`created+26h` reads ABSENT, `created+9h` reads NEW, re-measure at your merge base) (ev/roster_carry.txt).
  - The body names that SHA and `Carry: R10-CI-LAYOUT-P2`.
  - `carry_audit.py check --body` gives `3 routed, 0 unrouted, 0 bad destination(s)`.
- Head named in body: the `## Head` section names 48e8c29b7ffe23df442d563b7ae81d81e7475d4e. It describes the main merge on top of authored head 43bc60d2e, and `git diff af9face2d HEAD -- tests/nightly_status.py tests/entities.py` is code-identical, per the body.
- Class: the body's rule `grep -rlI "event=schedule\|actions/workflows/" tests tools .claude .github` returns 12 files at this head, not the body's 9. The 3 extra files came in with main after the body's base de69745ff: `tools/audit/seat/ci_probe.py` (dispatches), and `tools/ci/gate.py` and `tools/ci/prelude.py` (`ci.yml/runs?head_sha`). None of them states a schedule cause, so all three are outside the class. `grep "disables schedule\|no recent activity"` matches only this diff's own historical comment and docstring.
- `VERSION`, the manifest, `RELEASE_NOTES.md`, the claim files, the budgets and `tests/closures.json` are untouched. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Merge: `git merge-tree --write-tree origin/main 48e8c29b7` gives rc 0 and tree 118bc0387, with no conflicts and no MERGE-CLAIM lines (ev/merge_tree.txt).
- CI on this head, from the check-runs API with filter=all, all concluded: 31 success, 9 skipped, 1 failure (ev/check_runs_final.tsv).
  - The one red is `nightly-status` (concluded 22:47:47Z). The body's `## Red checks` answers it: the base copy of the reporter grades this PR and reads the false ABSENT this PR fixes, and the cheaper detector is the fixture pair this diff lands.
  - `pr-contract` run 120133363603 started at 22:48:04Z, after that red concluded, and succeeded.
  - fast (3.14), closures, coverage, coverage-ratchet, instrument-self-tests, browser, mutation, CodeQL and wave-script all succeeded.
- Heavy runs were not re-run; I cite CI's instead, per contract step 11.
