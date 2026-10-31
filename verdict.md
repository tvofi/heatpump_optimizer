Fix review: blocked eeb947e513fb1b43bd81946e3818f51195e33c48 defect: a bounded give-up in flock-wrap's renew-refused re-queue deletes the held- witness, so the seat's next leased script FAILS instead of the named-unrun SKIP

bus-nonce: a15392239e81a14d0ef49efafb1845ab

## Round

Round 1. Measured at head eeb947e513fb1b43bd81946e3818f51195e33c48 (code head 2327669181a6b5efdd25d8b8cfd5e00d949f4100, plus the delivery-row commit), merge base 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3, from detached worktrees at both SHAs. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract in force is the one I read.

## Block

The PR's two lease carries (P206, the wait bound; P211, the lapsed own lease) combine into a new failure, against P211's own constraint (a lease artifact must not fail a command for a label that held the lease).

- `tests/gate_lock.py` `flock_wrap`, the `except RenewRefused` arm: it calls `release(label)`, and `release` now also removes `held-<label>`. It then calls `take(..., wait_bound=wait_bound)`. If that bounded wait runs out, `WaitBoundExceeded` escapes and `_bounded` exits 76, but the witness is not re-marked. The lapse arm two lines below re-marks it (`release(...); _mark_held(...)`); this arm does not.
- What happens: a seat holds the lease under `HPO_GATE_LOCK_LABEL`, another label's ticket waits, and that label then holds the lease past the awaited script's bound. `run.sh` gets `SKIP: tests/stress.py (waited past its bound ...)`, which is right. The next leased script, `tests/harness_headers.py`, then goes to `flock-wrap`. `renew` raises `lease held by w, not seat`, and with no witness the lapse arm re-raises. The result is `gate_lock: flock-wrap refused, seat holds no lease`, rc 1, and `>>> FAILED: ... tests/harness_headers.py`. The manifest has `main-002 1 ... harness_headers.py`: a red gate from a lease artifact, not the sanctioned named unrun. Evidence: `ev/runsh-requeue-edge.txt` (the real `leased`/`run_always`/`scope_script` taken from this head's `tests/run.sh`, a scratch lock dir, and both recordings set to 3 s in a scratch `closures.json` so the bound is short). The same at module level: `ev/requeue-bound-edge.txt`.
- Control: the same scenario with one added line, `_mark_held(lock_dir, label)` after the `release` in the `RenewRefused` arm, gives `#skip tests/stress.py` and `#skip tests/harness_headers.py`, both named unrun (`ev/runsh-requeue-edge-control.txt`). The unbounded path (`wait_bound=None`, every caller before this PR) never reaches this state, because its `take` eventually succeeds and re-marks. So the defect is new with this diff.
- A repair owes a `_wait_cases` row for this sequence (re-queue, bounded give-up, next `flock_wrap` for the same label goes back into the bounded queue, not rc 1), and a mutant that drops the re-mark. That row would also be the first pin on the cross-call witness contract.

## Findings

- `tests/run.sh` `leased()`/`run_always()`: no test pins the new P206 mapping. Deleting the whole `if [ -e "$one.waited" ]` block survives every committed check, and then the run records `main-001 76 ... stress.py` as a failure, not a skip (`ev/runsh-mutant-nomap.txt`). The behaviour at the head is correct (`ev/runsh-skip-demo.txt`: `SKIP: tests/stress.py (...left to CI, named unrun)`, manifest `#skip tests/stress.py`). But the carry's "never a silent pass" constraint is only pinned in `gate_lock.py`, not where the lane decides pass or skip. The repair round the Block opens should add a run.sh-level row, or an entities/self-test arm, that drives `leased` with the marker present and absent. Carry: dismissed: owed by this same pull request's repair round, which the Block above already forces; R10-PREPR-CAP's roster entry reads `resume.stage done`, so it is not a live destination for carry_audit
- `tests/run.sh` lane mode (`JOBS>1`): a script that waited past its bound prints `[hh:mm:ss] ok <script> (5s)` on the console before `run_always` rewrites its log to the SKIP note (`ev/runsh-skip-demo-jobs2.txt`). The manifest is right (`#skip`), but the progress line reads as a pass. It is cosmetic, and the fix is to compute the status word after the marker test. Carry: dismissed: cosmetic, the manifest and accounting are correct; it belongs in the Block's repair round of this pull request, whose group's roster entry reads done
- `held-<label>` witnesses are never cleared for a label that is abandoned without `release` (its lease is stolen as expired or orphaned by another label). A later reuse of the same label is then treated as "held once", and `flock-wrap` takes the lease and leaves it held after the run. Carry: dismissed: the lease it leaves still expires at LEASE_SECONDS and is orphan-stealable, labels are per-topic, and the files are zero-byte; recorded so the next seat touching the witness knows its lifetime is unbounded.

## Evidence

Requirement by requirement, at the head:

- (1) Slot pool (already on main at the base, as the body says; `take_slot`, `HPO_HEAVY_SLOTS`, `holding_slot`, and the `export HPO_SLOT_LABEL` in prepr step 1b are all present at 7539d1675). I re-ran the measure-first evidence on a scratch lock dir (`ev/slot-measure-first.txt`):
  - p1..p4 print `taken slot=0..3`;
  - `p5 --no-wait` prints `BlockingIOError: all 4 heavy slots held`;
  - a blocking p5 queues (`waiting for a heavy slot`), and after `slot-release --label p1` it prints `taken slot=0`;
  - `HPO_HEAVY_SLOTS=9` gives `heavy_slots()` 4 (clamped);
  - `HPO_SLOT_LABEL=prepr-1` gives `holding_slot() True`;
  - `needs-lease` answers `lease` (stress.py), `none` (structure.py) and `slot` (features.py).
- (2) P206: `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept` prints `ALL 40 gate lock acceptance checks PASSED`, 7 of them new (`ev/gate_lock-accept.txt`).
  - Mutants (`ev/mutants-own.txt`), all killed: bound test -> `if False` (the run fails rc 1; the body said it hangs, rc 143 under `timeout 60`, and here the 60 s holder lease expired first, which is still killed); marker touch removed; `return WAIT_BOUND_RC` -> `return 0`.
  - The uncontended null holds: `ev/runsh-uncontended.txt` gives `STRESS RAN`, manifest rc 0, no lease left.
  - The slot arm of `leased()` is untouched, and `LEASE_SECONDS` and `renew()` are not in the diff.
  - Bound = max of the caller's scope scripts' recorded seconds (936.3 for stress.py), else `LEASE_SECONDS`, as carry 0 words it ("the awaited script's recorded duration when the caller names one").
- (3) P234/V148: `bash tools/pr/prepr.sh --self-test` at the head prints `437 passed, 0 failed`, rc 0 (`ev/prepr-selftest.txt`). The mutant restoring bare `python3` in `copies_line` prints `434 passed, 3 failed`: the venv control, the "ran under that venv" row and the HPO_RECORDER_PYTHON null control (`ev/prepr-mutant-bare-python3.txt`), matching the body. The no-interpreter row (rc 1, line names `seat_venv.sh`) and the one-resolution cache row pass.
- (4) P211, mutants (`ev/mutants-own.txt`), all killed:
  - drop the lapse arm: `RuntimeError: no live gate lease to renew`, rc 1;
  - drop the witness test: `a label that never held one is still refused` FAILS;
  - drop the waiter test: `ran=True` plus the never-held row FAIL.
- (5) P309 fold, carry_audit:
  - `python3 -I tools/audit/carry_audit.py --self-test` prints `211 checks, 0 failed`.
  - Mutants: drop the strip (`OWED_CARRY.search(text)`) fails the quote and code-span rows; drop the arm fails the owed-carry row and its routed null control; drop only the quote strip fails the quote row.
  - `python3 dev/audit/harnesses/r10_carry_parser_mutants.py` prints `RESULT sites=167 unmapped=0 mutants=241 survived=0` (`ev/carry-mutants.txt`).
  - Failing-test row on da4e6e9ea:BODY.md: the base prints `0 finding item(s)`, rc 0; the head prints `UNROUTED body item c78ecb78 [owed carry]`, `1 unrouted`, rc 1. With ` Carry: R10-FLY-TRAIN-DEFAULTS` appended to that paragraph it prints `1 routed, 0 unrouted`, rc 0 (`ev/3010-*.txt`).
  - `node tools/policy/field_coverage.mjs` prints `FIELD COVERAGE ok`, with `carry_audit owed-carry` declared.
  - The prepr.sh step 7e WHY now names fix-review step 10 and process state (c), and cites `dev/audit/rca/R10-RCA-JIDOKA-YIELD.md`.
  - The RCA document is the report after its first paragraph. It has a title line added, the trailing RESULT line dropped, and one sentence updated from "Whoever builds M1 or M2 corrects it" to "M1's pull request (R10-PREPR-CAP) corrects it". `tests/entities.py` prints `ALL 2493 ENTITY CHECKS PASSED`, so no new classification is owed (`dev/audit/` INERT).
- (5) Corpus null control, re-derived over the 263 `handoff-body/*` tips at review time (`ev/corpus-control*.txt`, `ev/corpus-items.txt`; this instrument is my own, `corpus2.py`/`corpus3.py`, counting unrouted `[owed carry]` items by importing the head's `items()`):
  - With the strip: 10 bodies and 34 unrouted items flip. Without it: 11 bodies and 32 items. The probe's own report body (`r10-rca-jidoka-yield`) flips only unstripped (2 items), as required.
  - Of the probe's 9, fly-train-defaults, fly-openpr-atomic, orch-planpage, sav-comfort, sav-comfort-r2, sav-comfort-r3 and train-overlap-grade still flip. Train-overlap-grade now has 1 item, not 9, because its tip moved on 2026-10-31. Ux-health-p2 is now routed, and cop-partload-p2's tip moved on 2026-10-31 and no longer flips.
  - New flips are flow-body-only, flow-record-pitch and roster-schema (21 items, every one a `Carry N: ... not built` line); each item I read is a real owed carry.
  - The strip is not purely a narrowing. It widens 4 items (roster-schema 1245e0ef, 81ea9a8c, bec62eae; fly-openpr-atomic ccdea0e7), because a removed code span holding a `.` no longer cuts the 80-character window. Each widened item is a real owed carry, so this is noted, not a defect.
  - The body's `24 items in 11 bodies` I could not re-derive under any reading I tried (any-status owed-carry items with the strip: 36 in 12 bodies; unrouted: 34 in 10). It is not verified.
- (6) The RCA (`handoff-body/r10-rca-jidoka-yield` c8f3acd99) names M1 for this group; the PR implements it, with the fixture, mutants and field_coverage registration the report says it owes when built. The body names M2 (P310, landed under R10-FLY-RELAY-REVIEW-FF) and shape B (P311) and states that the roster excludes both from this group, so the body does not silently omit either.
- Policy files in the diff: `dev/governance/rules/gate-scoping.md` and `dev/governance/roles/nudge.md` need the owner's approving review (noted, not blocked on). `node tools/policy/rules_sync.mjs --check` prints `RULES-SYNC ok`. `node tools/policy/policy_lint.mjs --budgets` exits 0. The gate-scoping diff also drops five issue citations (#1091, #1099, #1095, #1054, #2373, #2375) to stay inside the token cap; that is the owner's call with the rest of the wording.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc 0; no `*_budgets.json` is in the diff. VERSION, the manifest and RELEASE_NOTES.md are untouched. Both claim files are byte-identical to origin/main (`ev/untouched.txt`). The delivery row `dev/programme/delivery/3051.md` is in the three-dot diff.
- `git merge-tree --write-tree origin/main eeb947e5` (origin/main c3a47e565, 19 commits past the base) gives tree f593f977e, rc 0, with no conflicts (`ev/merge-tree.txt`).
- Body head: the body names eeb947e513fb... as the head, with code head 2327669181 as its parent; that matches what I measured.
- CI: `python3 tools/audit/seat/merge_train.py classify eeb947e5` printed `GREEN eeb947e513fb1b43bd81946e3818f51195e33c48 pending: none red: none` (rc 0, 19:00:26Z; `ev/ci-classify.txt`). No gate check went red on this head, so fix-review step 11 owes no answer. The head re-read at 19:01Z is still eeb947e5 (`origin/fix/r10-prepr-cap`). The scoped-gate MODE line is CI's to print and is not re-run here (fix-review step 11: cite CI's heavy runs).
