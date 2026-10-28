Fix review: blocked cd7dc09a8b2214e3392cdc5a157f41b5cd04bc68 class-open: the agreement lane (prepr.sh step 3f4, CI's governance / wave-script) and ref_privacy.py --check are carried to R10-FLY-CIPREDICT-LAYOUT with controls before the branch was cut, and are neither in the diff nor dispositioned in the body

bus-nonce: a27d6c562254ee2219692cab721e5de5

Round 1 of review for this PR. Measured head `cd7dc09a8b2214e3392cdc5a157f41b5cd04bc68` (still the branch head when this verdict was written, `git ls-remote`); merge base with origin/main `ac5788f2617755631f14e4d1a31efab0e47aa820`.

## Block

The group's roster entry (`handoff/audit-r10-roster` at `78dce1d51`, `dev/programme/rosters/wave-r10-groups.json`, group `R10-FLY-CIPREDICT-LAYOUT`) carries four items (`ev/roster-carries.json`). The body answers only the first one, #2554's layout guard. Two more were appended to this group by `roster_edit append-carry`: `7caf190ba` at 2026-10-23T21:44+02:00 (the #2671 round-3 carry) and `42e45f420` at 2026-10-24T00:00+02:00 (the #2671 root-cause seat's correction, R10-RCA-2671-WAVE-SCRIPT). Both landed before the authored code head `6965c36b4` was committed (2026-10-24T10:30Z) (`ev/carry-timeline.txt`). They ask for:
1. an agreement-lane arm that reproduces CI's wave-script restore, with a control that fires on #2671's `338c9ba49` merged into `fd7e289d0` (unregistered=3, rc 1) and a null control on #2669's `0506a55b2` merged into `e6dd46277` (rc 0); and
2. a `tools/audit/seat/ref_privacy.py --check` arm (governance.yml:424, instrument-self-tests), which fires at `338c9ba49`.

The body defines its class as "a CI command that `prepr.sh` runs before the PR exists but the handoff does not predict". Its enumeration rule is `grep -nE '^[a-z_]+_line\(\) \{' tools/pr/prepr.sh`, and it returns 9 functions. The rule misses prepr.sh step 3f4 (lines 3003-3014), which runs the agreement lane and is not a `*_line` function. So the body's own class has a seam that its rule does not return, that the diff does not close, and that the body does not disposition. `grep -n 'agreement\|ref_privacy' tools/pr/ci_predict.py` at this head returns nothing. `ref_privacy --check` falls outside the body's narrower class, but it is a carry routed to this group, and the body says nothing about it. If this merges as it is, the group closes with two routed carries silently dropped.

Repair: implement both arms with the controls the carries name. Or disposition each one in the body with a `Carry:` to a group that accepts it (the root-cause seat already routed the lane deadlock to R10-MERGE-SUBJECT-HARDEN). Also widen the census rule so it returns step 3f4.

## Findings

- Surviving mutant M8: `layout.guard(root, manifest, <HEAD~1>, "HEAD")` in place of the merge base `base` passes the self-test (rc 0). Every plant is one commit on its base, so the self-test never separates the merge base from the parent commit. My own both-ends probe shows that the head handles a plant followed by a second commit correctly (`twocommit` row, `ev/both-ends.txt`), but no in-tree case pins it. Repair: a two-commit plant case. Carry: R10-FLY-CIPREDICT-LAYOUT
- Surviving mutant M6: reading the manifest from the worktree (`(root / layout.MANIFEST).read_text()`) in place of `show(root, "HEAD", layout.MANIFEST)` passes the self-test. The body says the arm "uses HEAD's tests/layout.json", but no case leaves an uncommitted manifest edit for the self-test to see. Carry: R10-FLY-CIPREDICT-LAYOUT
- Surviving mutant M7: replacing the `LAYOUT UNREADABLE` return with `return []` passes the self-test. The body says that a guard that raises "prints LAYOUT UNREADABLE and also sets rc 1", but no case pins this. Carry: R10-FLY-CIPREDICT-LAYOUT

## Evidence

- Self-test at the head: `ci_predict self-test: 0 failed`, with 4 layout cases ok (`ev/selftest-head.txt`), on Python 3.14.7 at /opt/hpo/venv-ci.
- Mutation proof re-run (`ev/mutants.txt`, file restored after each mutant): M1 to M5 reproduce the body's table exactly. M1, M2 and M5 fail the two red cases with rc 0. M3 fails the staged-not-committed null case. M4 fails the two red cases because the repair line is missing. M6, M7 and M8 are my own mutants and survive (see Findings). The body's M1 to M5 table is verified.
- Both ends (`ev/both-ends.txt`), my own driver, in a `--shared` clone of the head, against CI's `tests/layout.py --guard` (a plain `tests/layout.py` run includes the guard and is the `run_always` line at tests/run.sh:563). Plant path `.claude/workflows/agreement.mjs`, the same as the body's. RESULT lines:
  - base predictor: re-add rc 0 against guard rc 1; citation rc 0 against guard rc 1; null rc 0 against guard rc 0; two-commit re-add rc 0 against guard rc 1.
  - head predictor: re-add rc 1 against guard rc 1; citation rc 1 against guard rc 1; null rc 0 against guard rc 0; two-commit re-add rc 1 against guard rc 1.
  - Each red row at the head prints one `PREDICT tests / fast (3.14) LAYOUT ...` line plus the repair line. My grep for " LAYOUT " counted both, which is why it shows 2. This matches the body's both-ends table.
- Figures re-derived at this head against merge base `ac5788f26` (`ev/figures.txt`). The body took its figures against `145bfe197b9e`, and the merge commit `d9a6f2f2d` changes neither of the PR's files.
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
  - `STRUCTURE RATCHET PASSED`
  - `Architecture score: dS +0.0000 NULL`
  - `throwaway_git: 0 raw ... refused, 0 stale`
  - `layout: GUARD: 0 refusal(s)`
  - `CI PREDICT: no closures or fast red predicted`
  - `selftest_wiring: 93 self-testing, 93 wired, 0 unwired`
  - census grep: 9 functions, as the body says.
- Not re-run: `entities.py` (2425 checks), `harness_headers.py`, `closure.py selftest` and `carry_audit` on the body. These are CI's to cite.
- VERSION, the manifest version, RELEASE_NOTES.md and the claim files are untouched (three-dot diff).
- `git merge-tree --write-tree origin/main cd7dc09a8b2214e3392cdc5a157f41b5cd04bc68` exits rc 0 with tree `496c9d619`: no conflict (`ev/merge-tree.txt`).
- The head SHA in the body's `## Head` section is `cd7dc09a8b2214e3392cdc5a157f41b5cd04bc68`, the head I measured.
- CI on this head (check-runs API, ~13:56Z): most jobs are queued. arch-score, prelude and refresh are success, the rest are skipped. Nothing is red, so step 11 has nothing to answer yet. The workflows have not concluded.
- The body's forward-carries go to R10-FLOW-JIDOKA and R10-POLICY-GATE-SCOPING, and both groups exist on the roster. They do not settle the Block above.
