R10-FLOW-AUTOTRAIN. A verdicted pull request now enters the merge train through #2772's `add`. There are two ways in: an event when a merge verdict is posted, and a slow backstop sweep for any head the event missed. No train is pitched on a timer, and no agent's turn is involved. Part of #2715.

- **Admission.** `Train.admit_add`, #2772's admission seam, gains a `verdict` rule (`Train.add_verdict`). It runs on a `main` base, after `open`/`base` and before `carry`. The rule is the queue builder's own read, factored out as `Train.posted_verdict`: the newest approver-App `Fix review:` comment must be `verdict/<pr>`'s posted tip and must say `merge` at the added verdict. The grammar is read only through `proof_watch.parse_verdict`, which `orchestrator_tick.py` also reads.
- **The event.** `bus.sh`'s `post_verdict` ends with `train_add`. For a merge verdict it has just posted, that runs `merge_train.py add <pr> <verdict-head> --auto` against `$HPO_BUS_TRAIN_STATE`, which is off when unset. A refused add never fails the post. `add --auto` gives a started train `train.sh --bot-prs --approval-carry --pre-flight` (`AUTO_TRAIN_FLAGS`).
- **The backstop.** `merge_train.py sweep` holds while the obligations ledger has an open `train-stop`. Otherwise it hands every head `build_queue` admits to `train_add`, once per head (`sweep-added.json`). `train_add` holds the queue lock, applies the ALREADY rule and `admit_add`, and keeps one train per state dir, reading `queue.open` and then `train.pid`. So the head joins the live train's next batch, or starts the first train. `tick_loop.sh --sweep` runs the sweep every `HPO_TICK_SWEEP_EVERY` seconds (default 1800).
- **Removed:** the hourly `pitch`, `launch_train`, `live_train` and `tick_loop.sh --pitch`. `launch_detached` (#2772) is the one launcher.
- **Closures (this pass).** `merge_train.py` now imports `tools/audit/seat/proof_watch.py` and `tools/audit/seat/ledger.py`. `tests/entities.py` reaches both, but both were inside the INERT `tools/audit/` prefix, so `tests / closures` reported them UNDER-SCOPED and `closures-autofix` refused to merge an INERT file that is read. Both now sit on `tests/closure.py`'s `INERT_EXCEPT`, as `merge_train.py` already does, and `tests/closures.json`'s `tests/entities.py` entry is re-recorded on Linux with `--single`.
- **P96(b) pin (this pass).** #2772's `admit_add` already admits a carried single, so this is a pin rather than new code. A new self-test arm drives a real throwaway repository through the real `app_approve.sh --carry`. The entry's verdict is an ancestor of its head, and main's automatic merge is the only gap. The arm requires the entry to be spooled for the live train's next batch, and requires the carry to be read while the queue lock is held. The null control is a head carrying a commit of the branch's own past the verdict, which is refused as `carry`.

Alternatives considered:

- (a) The event could call `train.sh add` with its flags spelled out in bus.sh. That would make a second copy of the started train's flags. `add --auto` keeps the single copy, `AUTO_TRAIN_FLAGS`, which the sweep shares.
- (b) The sweep could skip any head already in the live train. That would duplicate `train_add`'s ALREADY rule. The sweep instead remembers only what it handed over itself.
- (c) The closures red could be answered by removing the imports, re-inlining the grammar and the ledger read in `merge_train.py`. That is the two-reader shape `agreement_py` refuses. The INERT_EXCEPT route already used for `merge_train.py` keeps one reader and makes an edit to either file select `tests/entities.py`.

## Head

The code head is `ea464fe68728c2960e8a42cf00b323901938ac23`. Its merge base is `973618e6f9410f7864993837cfc6153bb9b21fca`, which was origin/main's tip when this pass merged it (committed 2026-10-25T05:51Z). The head is the r3 code head `3cc94a93c` plus three commits: `667d85c22` (`git merge origin/main`, no conflict), `e3897d014` (the P96(b) pin and harness mutants C1 and C2) and `ea464fe68` (the closures classification and the re-recorded `tests/entities.py` entry). origin/main has since moved to `21a1e04a7`; this was read at 2026-10-25T07:18Z. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so per fixer.md step 6 the head is not merged again. Every figure below was taken at this head in this pass.

## Mutation proof

- **Admission, sweep, event and loop:** `bash dev/audit/harnesses/r10_flow_autotrain_mutants.sh` plants one mutant per rule and runs the owning self-test from the committed tree: `merge_train.py`, `bus.sh`, `tick_loop.sh` or `orchestrator_tick.py --self-test`. It then restores the file. The kill rule: the self-test's last line reports one or more failures, and `PATTERN NOT FOUND` is absent. Result at the head: 43 mutants planted, 43 killed. Of the 43 non-M0 `== <id>:` lines, 0 read `0 failed` or `PATTERN NOT FOUND` (`grep "^== " | grep -v M0 | grep -c " 0 failed\|NOT FOUND"` printed 0). Baseline (M0): `merge_train self-test: 318 checks, 0 failed; tick_loop self-test: 17 checks, 0 failed; bus self-test: 74 checks, 0 failed`. Each rule and the arm that kills it:
  - **Refused add, rule named** (`admit_add`). V1 to V6 cover the `verdict` rule: off, another sha, another comment id, comment not filled, unreadable bus, bus tip ignored. R1 to R7 cover #2772's `shape`, `open`, `base`, `carry`, `row`, `budget-raise` and `policy`. Each fails its `admit_add refuses by its \`<rule>\` rule, naming it` arm, or the comment-fill arm for V4.
  - **Carried single into a live train** (P96(b), this pass). C1 runs the add without the queue lock and fails the CARRIED arm (`held == [True]`) as well as #2772's RACE arm. C2 never reads the carry and fails the null-control arm "a head carrying a non-main delta past its verdict is refused by the `carry` rule". R4 fails that arm too.
  - **Add during proof lands in the next batch.** S7 turns off the live-train spool branch and fails both "sweep while a batch is in proof ..." and #2772's "add, a train live: the entry is spooled for its NEXT batch".
  - **Sweep exactly once, never a second train.** S1 and S6 fail "sweep: EXACTLY ONCE"; S6 also fails "a new verdict at a moved head is a new entry, added once". S2 to S5 and S8 cover a failed start, a refused-add retry, the ledger hold, the started train's flags, and `--auto` combined with `--`.
  - **Event add.** B1, B2 and B3 fail "with no HPO_BUS_TRAIN_STATE a posted merge verdict ... adds nothing", "a posted blocked verdict adds nothing" and "a posted merge verdict is added to the train at its head".
  - **Loop.** T1 to T3 fail the `--sweep` arms.
  - **Builder.** A1 to A12 fail the `queue:` arms. G1 and G2 re-inline the grammar and fail the two `parse_verdict` arms; under each, `agreement_py --run` prints `unregistered=1`.
- **Closures classification (this pass).**
  - Deleting the two `INERT_EXCEPT` lines from `tests/closure.py` makes `PYTHONPATH=tests/hastub python3 tests/closure.py check --in-dir <rec> --partial` exit 1. It prints "files on the INERT list are inside a recorded closure ... tools/audit/seat/ledger.py, tools/audit/seat/proof_watch.py". After restoring them it prints "closure: committed closures cover every file this run touched".
  - Here `<rec>` is `./tests/derive_closures.sh --single tests/entities.py --record-only --out-dir <rec>`, the same recording at the same tree.

## Null control

- **Before the fix.** The same recording, checked against the committed `tests/closures.json` before the re-record, printed "UNDER-SCOPED: tests/entities.py really reads 3 file(s) the committed closure does not list: tools/audit/seat/ledger.py, tools/audit/seat/proof_watch.py, tools/ci/sweep.py". CI's closures job 121037861937 at `f3bd78c35` named the first two. `tools/ci/sweep.py` arrived from main after that run: `tools/ci/gate.py` imports it.
- **The P96(b) pin.** The carried single's admitted twin is the null control's pair: the same verdict and the same live train, at a head whose only gap is main's automatic merge, is ADDED. #2772's own arm "admit_add: a green, rowed, carried head is admitted (null control)" still passes.
- **The base.** At merge base `973618e6f`, `merge_train.py sweep` prints `invalid choice: 'sweep'`, and bus.sh holds no `train_add` (`grep -c "train_add\|HPO_BUS_TRAIN" tools/audit/seat/bus.sh` gives 0).

## Figures

- Self-tests at the head:
  - `python3 tools/audit/seat/merge_train.py --self-test`: 318 checks, 0 failed.
  - `bash tools/audit/seat/bus.sh --self-test`: 74 checks, 0 failed.
  - `bash tools/audit/seat/tick_loop.sh --self-test`: 17 checks, 0 failed.
  - `bash tools/audit/seat/train.sh --self-test`: ok.
  - `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 214 checks, 0 failed.
  - `python3 tools/audit/seat/proof_watch.py --self-test`: 40 checks, 0 failed.
  - `python3 -I tools/audit/seat/ref_privacy.py --self-test`: 92 checks, 0 failed. The diff adds no push site.
- Mutants: `bash dev/audit/harnesses/r10_flow_autotrain_mutants.sh` planted 43 and killed 43, under the kill rule given in Mutation proof.
- Closures: `PYTHONPATH=tests/hastub python3 tests/closure.py check --in-dir <rec> --partial` prints "committed closures cover every file this run touched" at the head. `git diff 973618e6f HEAD -- tests/closures.json | grep '^[+-] '` prints five added lines and no removed ones. Three go into the `tests/entities.py` entry in this pass: `tools/audit/seat/ledger.py`, `tools/audit/seat/proof_watch.py` and `tools/ci/sweep.py`. The other two are the group's two harnesses, which earlier commits on this branch listed in `inert_reads.tests/harness_headers.py`.
  - The re-record merged with `closure.py merge --in-dir <rec> --partial --allow-failures`. The recorded run reached its summary line (`2 of 2440 ENTITY CHECKS FAILED`), so every import and read was exercised.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL`, because `tests/closure.py` changes the gate itself. Per fixer.md step 5 that is a diff the gate cannot scope, so these ran locally and the rest is left to CI:
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `2 of 2440 ENTITY CHECKS FAILED` at the head and at merge base `973618e6f`. The FAIL-line sets, sorted with their bracketed detail stripped, are identical (`diff base head && echo IDENTICAL` printed IDENTICAL). The two counted failures are the `hb:positive_control` py-spy checks, which this container cannot satisfy.
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`, under the gate lease.
  - The run_always set: `python3 tests/closure.py selftest` (`ALL 117 closure shrink pins PASSED`), `python3 tests/layout.py` (`layout self-test: ok`) and `python3 tests/env_drift.py --claims-only 973618e6f` (`claims hygiene: ... ok`).
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Agreement: `python3 -I tools/policy/agreement_py.py --run` gives `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`, with 18 closure files, 18 of them covered by the wave-script restore list.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 973618e6f941`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 96 self-testing, 96 wired, 0 unwired.
- `python3 tests/throwaway_git.py --check`: 0 refused. The new self-test builds its repository through `throwaway_git_init`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused.

## Red checks

- `tests / closures`, red at `f3bd78c35` (job 121037861937). The cause: `merge_train.py` began importing `ledger.py` and `proof_watch.py`, which sat under the INERT `tools/audit/` prefix, and `tests/entities.py` reaches both. This diff repairs it (`ea464fe68`). The cheaper detector is `./tests/derive_closures.sh --single tests/entities.py --record-only` before the handoff, or prepr step 6b with `PREPR_RECORD_CLOSURES=1`. Its standing cost is about 19 minutes of `entities.py` under strace on this seat box, measured by this pass's recording. `tools/pr/ci_predict.py` does not see it, because it reads no recording ("a data-file read is not seen").
- `tests / closures-autofix`, red at `f3bd78c35` (job 121046427856), the same cause: the bot reported skip-merge-failed, because merging the recording would list an INERT file in a closure. It is repaired by the same commit, and the cheaper detector is the same.
- `tests / nightly-status`, red on main's ancestry. It grades `main`'s nightly lane, not this head (`merge_train.py`'s default `--ignore-red`). This diff did not turn it red, and the detector that grades it is the nightly itself.
- `tests / ci-ratchet`, which may be red on main's push runs. GitHub's repo-wide artifacts listing returns 0 bytes, and a hotfix is in flight. It is not this branch's red, and this diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

1. Incoming carry P96(b), on R10-FLOW-AUTOTRAIN: discharged in this diff by a pin, the `add, a train live: a CARRIED single ...` arm plus its null control in `_add_self_test`, killed by harness C1, C2 and R4. #2772 had already implemented the admission, so no production line was needed. Carry: dismissed: discharged by this diff
2. Incoming TRAIN-UPGRADE carry, on R10-FLOW-AUTOTRAIN: discharged by the code at this head. `Train.admit_add` is the seam the `verdict` rule extends. `launch_detached` is the one launcher: `grep -c "launch_train" tools/audit/seat/merge_train.py` gives 0. `train_add`'s live-train check reads `queue.open` and then `train.pid`, under the queue lock (the "add beside a train.sh still holding train.pid with no queue open" arm). Carry: dismissed: discharged by this diff
3. The live sweep and the event add are off by default (`tick_loop.sh --sweep`, `HPO_BUS_TRAIN_STATE`). Under the roster's card-1 acceptance, the first real load runs with the merge seat watching. Until then, nudge.md step 3 ("when no train is running") still describes the hand pitch. Once the job is verified, step 3 drops that clause and names `sweep` and the event add. Control: diff nudge.md step 3 against `sweep` and `sweep_template.md` item (3); no contradiction remains. Carry: R10-POLICY-ROLE-PACK
4. R10-ORCH-BEATD's job table names a `pitch` job. That job is now `merge_train.py sweep --state-dir <dir> [--mandate M]`, a one-shot whose last line is `SWEEP HELD|REFUSED|DONE` (rc 2 only on REFUSED), run every 1800 s. bus.sh's `HPO_BUS_TRAIN_STATE` on the confirming machine is the event. Nothing writes a ledger `train-stop` yet, so the beat's producer must run `ledger.py open train-stop <pr> <head>` on a `TRAIN STOPPED` line. Carry: R10-ORCH-BEATD

## Friction

none
