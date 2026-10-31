Closes #2267 (the slot pool, `prepr.sh` step 1b and `needs-lease`'s `slot` answer, was already on main at the base: `tests/gate_lock.py` `take_slot`, `slot-auto-lease`, `derive_closures.sh` and `run.sh` join `$HPO_SLOT_LABEL`; this pull request adds the four carries the dispatch folded into the group).

- Carry 1 (P206): `take()` gains `wait_bound`; `auto-lease` and `flock-wrap` take `--script <SCOPE_RUN file> --wait-marker <file>`. A `lease` waiter past the bound exits 76 with one line; `run.sh` `leased()` sees the marker and `run_always` records `#skip <script>` plus `SKIP: <script> (waited past its bound for the gate lease; left to CI, named unrun)`, never a pass. `slot` arm untouched; uncontended runs take no new branch.
- Carry 2 (P234/V148): `copies_line` runs the interpreter `recorder_python` prints; one resolution per run, cached in a file (`PREPR_RECORDER_CACHE`) shared with step 6a.
- Carry 3 (P211): `flock_wrap` retakes a lease that lapsed between commands for a label that held one (witness: a `held-<label>` file `take` writes and `release` removes); `renew()` and `LEASE_SECONDS` unchanged.
- Carry 4 (P309): `carry_audit.py` `[owed carry]` arm (M1) with its two `--self-test` rows and 4 harness mutants, the RCA landed as `dev/audit/rca/R10-RCA-JIDOKA-YIELD.md`, the WHY at `prepr.sh` step 7e corrected (process state c).

## Head

Code head 2327669181a6b5efdd25d8b8cfd5e00d949f4100 on base 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3 (origin/main unmoved at the last `git fetch origin main`).

## Mutation proof

- Carry 1, delete the bound test (`if wait_bound is not None and waited >= wait_bound:` -> `if False:`), `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept` in a copy of `tests/`: the run never returns (the waiter waits forever); `timeout 60` -> rc 143.
- Carry 3, delete the whole lapse arm (`except RuntimeError:` branch of `flock_wrap`): the `an expired own lease with no waiter refreshes and runs` row raises `RuntimeError: no live gate lease to renew`, today's rc 1. Delete only the `held-` witness test: `a label that never held one is still refused` FAILS. Drop the waiter test (`if mine and any(...)` -> `if False`): `one with a waiting ticket re-queues and does not run beside it` FAILS (`ran=True`) and the never-held row FAILS.
- Carry 2, `"$py"` back to bare `python3` in `copies_line`, `bash tools/pr/prepr.sh --self-test` in a copy: FAIL `a PATH python3 that cannot parse the tree is skipped for the parsing seat venv`, `and no-copies ran under that venv, not the bare python3` and `HPO_RECORDER_PYTHON naming a parsing interpreter is the one that runs (null control)`.
- Carry 4, `python3 tools/audit/carry_audit.py --self-test`: dropping the strip (`OWED_CARRY.search(text)`) fails `an owed-carry phrase inside double quotes is not read` and `... nor one inside a code span`; dropping the arm (`else "owed carry" if owed_carry(t) else ""` -> `else ""`) fails `an owed roster carry in an untitled paragraph is an unrouted [owed carry] item` and the routed null control. `python3 dev/audit/harnesses/r10_carry_parser_mutants.py` maps the arm: `I-owed-arm`, `I-owed-strip`, `I-owed-code`, `I-owed-quote` all killed; I-blead's and I-binh's patterns were re-anchored to the new text and are killed.

## Null control

- Carry 1: an uncontended `take` and every caller naming no `--script` pass `wait_bound=None` and take today's path; `a take within its bound still runs` and `the bound is the recorded duration, else LEASE_SECONDS` rows. The bound is `max` of the recorded seconds of the scope's scripts (`stress.py` is recorded at `tests/closures.json`'s `recorded.seconds`), so it is never shorter than the run waited behind.
- Carry 3: a run that never loses its lease takes `renew()` with no new branch; `a label that never held one is still refused` (also `tests/entities.py`'s `a seat label never taken fails at once; a held one re-queues behind a waiter`).
- Carry 4: #3010 r1 body (`da4e6e9ea` BODY.md) at base gives `0 finding item(s)` rc 0; at this head `UNROUTED body item c78ecb78 [owed carry]`, rc 1; with ` Carry: R10-FLY-TRAIN-DEFAULTS` appended: `1 routed, 0 unrouted`, rc 0. Corpus control: the strip is the narrowing; the probe's own report body (`handoff-body/r10-rca-jidoka-yield`) flips only in the unstripped arm (2 items), the stripped arm flips only real owed carries.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept` -> `ALL 40 gate lock acceptance checks PASSED` (7 new rows).
- `python3 -I tools/audit/carry_audit.py --self-test` -> `carry_audit self-test: 211 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_carry_parser_mutants.py` -> `RESULT sites=167 unmapped=0 mutants=241 survived=0`.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <da4e6e9ea:BODY.md>` -> `1 finding item(s): 0 routed, 1 unrouted` rc 1 (the same at the base prints `0 finding item(s)`).
- Corpus: for every `refs/remotes/origin/handoff-body/*` tip (250 at 2026-10-31), count items whose `why` is `owed carry` (the arm) against items `OWED_CARRY` matches with no strip: 24 items in 11 bodies flip with the strip, the probe report body flips only unstripped. Triage measured 223 bodies and 9 real catches; the tree has since grown (r10-flow-body-only, r10-flow-record-pitch, r10-friction-regression are new).
- `bash tools/pr/prepr.sh --self-test` -> see the committed run in the PR (this seat ran it at the head); the mutant copy with bare `python3` restored: result line in `## Red checks` is none, the control row names it.
- `node tools/policy/policy_lint.mjs --budgets` -> exit 0 (`.claude/rules/gate-scoping.md` at 794 tokens = its cap, 56 lines = base; `tools/audit/briefs/nudge.md` at 3814 = its cap); `node tools/policy/field_coverage.mjs` -> exit 0 with `carry_audit owed-carry` in the derived set.
- Measure-first (the pool, on a scratch lock dir with `python3 tests/gate_lock.py --lock-dir <d> slot-take --label pN --owner-pid <live pid>`): p1..p4 print `taken slot=0..3`; `p5 --no-wait` prints `BlockingIOError: all 4 heavy slots held`; after `slot-release --label p1`, p5 prints `taken slot=0`; `HPO_SLOT_LABEL=prepr-1` makes `gate_lock.holding_slot()` True, so a nested step does not re-acquire (prepr.sh step 1b and `run.sh` `leased()` read it).
- Class enumeration (fixer step 8) for Carry 4: `python3 -I tools/audit/carry_audit.py` over `handoff-body/*` as above; the shape A and B blocks of the RCA are its M2 (P310, landed elsewhere) and P311, out of scope by the brief.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Pending: `dev/governance/rules/gate-scoping.md` and `dev/governance/roles/nudge.md` are policy (owner review), and `tools/audit/carry_audit.py` is `@tvofi`-owned. One wording decision for the owner: `nudge.md` §8's `Do not start a fifth.` was dropped to stay inside the file's token cap, since the sentence before it already says a fifth queues and now says the lease, not the tick's count, is the cap. Reviewer: opus, independent of this seat; the dispatch owes it (this is the orchestrator's own instrument).
