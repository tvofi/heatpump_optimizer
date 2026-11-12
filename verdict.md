Fix review: merge 7ee0461a30e2c58d7e5f78c1fdaa13232325f88b

bus-nonce: cfb536a67702d5453447857937b0d48b

## Round

This is round 2, a handoff review of the fixer's repair. Round 1 blocked `38aee2235ae2dbc72ef1023e5baa27b8ffa1d619` (`verdict/3490`, probe `revt-r10-seat-script-output-02e6a9b4`). I reviewed the whole branch `ba544faa..7ee0461a` (3 commits, 13 files, +161/-9), not only the delta.

## Round-1 block, item by item

1. **Key lines dropped.** Answered. The keep-list `KEY_LINE` is replaced by the hide-list `QUIET_CHATTER` (9 members). To check it, I classified every production `log(` literal outside the self-tests by AST against `QUIET_CHATTER_RE` (`ev/hidden-literals.txt`, this reviewer's instrument). The only lines it hides are progress chatter:
   - the gh/git retry notes (`merge_train: `, :1638 and :1647);
   - the CI-wait and gate-deferral lines (:2014 and :2036);
   - the recarry start and progress lines (:2578, :2604 and :2610) and `#N overlap: recarry start` (:4102);
   - the success branches only of `released`/`deleted` (:2952 and :4207);
   - `grade ... ok` and `platform gate=green`.

   The failure lines `NOT released`, `NOT deleted` and `grade ... RED` print. So do every `#N MERGED`, OWED, `ci red=`, serial, STALE, OVERLAP, REJOIN, INFRA-RED, LEFT, QUEUE, `[MAIN-MOVED]` and `SKIP` line.
2. **Exit-code agreement asserted, not measured.** Answered. The self-test runs a seeded stop through `main` in quiet, `--verbose` and `TRAIN_VERBOSE=1` and asserts rc 1 in all three. B1, B2 and R5 below kill it.
3. **Quiet rules had no mutant.** Answered. Mutants of the round-1 survivors are now killed:
   - M5 → B1 (1 failed);
   - M6 → B2 (1 failed) and R5 (1 failed);
   - M7 → B3 (2 failed);
   - M4/M8 → B6 (1 failed) and B4/B5 (13/29 failed).
4. **SKIP lines lost to `train.log`.** Answered. `SKIP #<pr> <phase>:` matches no chatter member and prints on stdout. B8 makes a chatter member match `SKIP ` and is killed (3 failed).

## Findings

- Surviving mutant R6: changing `QUIET_CHATTER_RE.match(m)` to `.search(m)` passes the full self-test (654 checks, 0 failed). Under it, the key failure lines `NOT released wt-12 (rc=1: ...)` and `NOT deleted batch/t-1 (rc=1: ...)` are hidden, because the unanchored `(released|deleted) ` member matches inside them (`ev/r6-demo.txt`: match-hidden False, search-hidden True). The anchoring is correct at this head, so this is not a live defect: it is a test gap. Adding a `NOT released ...` spelling to the self-test's key-line tuple kills it; null control: the same tuple without it lets R6 survive, as measured here. Carry: R10-TRAIN-RESIDUE-P2
- Surviving mutant R2: removing `held.clear()` after the stop flush passes. The mutant is equivalent under current callers: each of the three production `TRAIN STOPPED` writers (merge_train.py:3042, :3837 and :4199) returns right after the line, so one `quiet_log` never sees a second stop. Carry: dismissed: equivalent mutant, at most one TRAIN STOPPED per quiet_log at every production writer
- Surviving mutant R7: `os.environ.get("TRAIN_VERBOSE") == "1"` → truthy also passes. The only difference is that `TRAIN_VERBOSE=0` would mean verbose, and the documented switch is `=1`. Carry: dismissed: differs only on undocumented env values, no key line or exit code changes
- The body says update_pr.sh and open_pr.sh "are not changed in this round", but carry 0 (owner-ordered) names both scripts. I read both (142 and 155 lines). Their own output is result and refusal lines (`BODY-ONLY`, `HEAD=`, `PR=… HEAD=…`, `ROWLESS`, `CLOSED`). Their bulk stream is prepr.sh's, run through app_push.sh, and prepr.sh is already quiet by default with `--verbose`/`PREPR_VERBOSE=1` (tools/pr/prepr.sh:18-20). So the owner card's convention reaches them already, and the body should say so instead of reading as a deferral. Carry: dismissed: the requirement is met by inheritance through prepr.sh's quiet default; no change owed in these two scripts

## Evidence

- Head reviewed: `7ee0461a30e2c58d7e5f78c1fdaa13232325f88b` (`ev/HEAD.txt`), the handoff tip. The body's `## Head` names the same SHA. Merge base `ba544faa2dd25b75b0129879112d6409affe9662`. Diff: `ev/diff.patch`.
- No review packet and no CI: no pull request carries this head yet (PR #3490 is at `580cef9e`), so I read no check runs at this head and no red at it is owed an answer.
- `git merge-tree --write-tree origin/main 7ee0461a`: rc 0, no conflict (`ev/mergetree.txt`).
- VERSION, the manifest, RELEASE_NOTES.md, `custom_components/` and `tests/`: untouched. No claim file or golden fixture is touched, so `env_drift.py` has nothing to compare.
- RESULT selftest-head: `merge_train self-test: 654 checks, 0 failed`, rc 0 (`ev/selftest-head.txt`).
- RESULT body mutants: all 8 killed, with counts matching the body: B1 1, B2 1, B3 2, B4 13, B5 29, B6 1, B7 2 (`ev/mut-1.txt`, `ev/mut-2.txt`). For B8 the body says 4 failed; I measured 3, but my spelling was `(released|deleted|SKIP) `, a different member and spelling from the body's, so the counts are not comparable. Both are killed.
- RESULT reviewer mutants: R1 1, R3 2, R4 7, R5 1 and R8 3 are killed. R2, R6 and R7 survive (see Findings; `ev/mut-3.txt`, `ev/mut-4.txt`).
- RESULT pr_bounded, all 12 self-tests at this head, rc 0 each (`ev/sh/`):
  - body_patch 109/0, bus 174/0, ci-watch 18/0, cloud-setup 22/0;
  - delivery_row 6/0, failure_logs 7/0, handoff_push 6/0, heartbeat 8/0;
  - merge_pr 22/0, seat_venv 27/0, tick_loop 27/0, train ok.
- Bound null: `PR_SELFTEST_SECONDS=1 bus.sh --self-test` printed `BOUND: the self-test passed 1 s` and returned rc 124 (`ev/sh/null-bound-bus.txt`).
- Body figures re-derived:
  - nine chatter members: `len(QUIET_CHATTER) == 9`;
  - 24 key-line spellings: counted in the self-test tuple;
  - 12 scripts with a one-line `pr_bounded` entry: the diff;
  - functions touched: `QUIET_CHATTER`, `quiet_log`, `wire_quiet`, `_parser` and `main`, plus the self-test block. No `Train` method is edited.
- Body `## Red checks` names reds on PR #3490's earlier head, not on this one. It quotes `merge_train.py owed-reds` as printing three names. Run live here, that command prints 23 names, `tests / fast (3.14)` among them. The set is read from the live ruleset, so the quoted three-name set does not re-derive now. Each listed red carries a written answer, so the trigger is answered whatever the set; pr-contract re-checks the body against this head's CI once the PR is updated.
- Harness: there is no committed finder harness for this group. The checks are the fixer's self-test entries. The AST classifier (`ev/hidden-literals.txt`), the mutant driver and the R6 demo are this reviewer's own.
- Architecture: the added code is two module-level functions and one constant before `class Train`, plus one call in `main`. No logic of `Train` changes, which matches the brief's "output calls only in merge_train.py".
