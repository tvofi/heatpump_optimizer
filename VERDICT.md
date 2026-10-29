Fix review: merge aaf1d39f9fd45b8fc39b375e44ab2f0bb4a20acd

bus-nonce: 7cecb048a79f94d312b5c0f6069c991d

## Round

Round 1 (the first fix review at this group's PR). Head measured: aaf1d39f9fd45b8fc39b375e44ab2f0bb4a20acd, still the PR head when this was written. The roles diff against main since the merge base (279578074) is empty, so the contract is current.

## Findings

- A surviving reviewer mutant in a line the PR does not name: merge_train.py main_green's blocking arm, `self.sleep(POLL_SECONDS)` after a successful infra re-run, replaced by `pass`, still gives `merge_train self-test: 344 checks, 0 failed`. The self-test's sleep is a no-op lambda, so nothing pins the wait between the re-run POST and the second `wait_ci` read. Without it, the second read can see the old completed red before GitHub has queued the re-run's check runs, and stop red anyway. The code is correct as written; only the pin is missing (ev/reviewer_mutants.txt). Carry: R10-FLOW-MAIN-GATE
- A surviving reviewer mutant: infra_rerun's `reran = reran or code == 0` replaced by `reran = True` still gives 344/0. No check plants a failed rerun-failed-jobs POST in the blocking arm. A failed POST would then cost one extra POLL_SECONDS sleep and one more read before the same red Stop. The impact is bounded to delay, and only the pin is missing (ev/reviewer_mutants.txt). Carry: R10-FLOW-MAIN-GATE
- A surviving reviewer mutant: `done.add(rid)` replaced by `pass` (no per-run de-duplication) still gives 344/0. Carry: dismissed: in effect an equivalent mutant. A second red context on the same run re-reads `run_attempt`, which a successful first POST has already moved to 2, so the attempt-1 test refuses the second re-run, and main's ruleset requires the one `gate` context anyway.

## Evidence

- RESULT mutation (PR's named twelve, the PR's committed harness dev/audit/harnesses/r10_seat_selftests_mutants.py, run by this reviewer at the head): `RESULT survivors=0`. Every one is KILLED, with per-mutant failure counts 2,1,3,4,1,1,1,1,1 (merge_train-25..33) and 4,2,1 (bus-1..3), which match the body's named failing checks (ev/mutants.txt).
- RESULT reviewer mutant reasons-unbounded (gate_outcome reads past the `##[error]` line): KILLED, 4 failed (ev/reviewer_mutants.txt).
- RESULT null controls at the head, unmodified: `merge_train self-test: 344 checks, 0 failed`, `bus self-test: 104 checks, 0 failed`, `cloud_dispatch self-test: 87 checks, 0 failed`. All three equal the body's figures.
- End to end, the real classifier with the exact argv bus.sh now passes (`merge_train.py classify <head> --repo tvofi/heatpump_optimizer`, which the self-tests stub out) ran at this head while CI was in flight and printed `WAIT ... pending: gate red: none`, rc=3. So the CLI accepts the arguments, and the `RED .* red: ` sed in bus.sh's refusal matches the line's real shape (ev/classify.txt).
- I checked the log format against gate.py: it prints `FAIL <why[0]>` then `why[1:]` unprefixed, unit names are `<workflow> / <job>` (jobs-API names), and RATE-LIMITED is followed by an `::error` annotation that renders as `##[error]`. gate_outcome's backward scan from the first `##[error]` matches all three. Any other or earlier `##[error]` makes it return None, which leaves today's red: it fails closed.
- False-positive probe for INFRA_STRINGS: the self-tests of gate.py, sweep.py, prelude.py, ghapi.py, proof_watch.py and merge_train.py print none of the three strings on a normal run, so a real self-test failure in those lanes is not read as infrastructure.
- Finder's harness: none exists. V142 and carry b87aa9e4 were triaged from instances, as the body discloses. The controls are the committed `_infra_self_test` (the stamp run 40596083060's shape, both reason orders, and the nulls) and bus.sh's four K15 (d) checks. I built no harness of my own beyond the targeted mutants above.
- Class (step 6): the body's seam rules re-run at the head. `grep -nE 'self\.main_green\(' tools/audit/seat/merge_train.py` returns three call sites, all through main_green's two arms, both of which call infra_rerun. The dispatch registry has one writer, bus.sh `dispatch`. Nothing is left open.
- Merge with main: `git merge-tree --write-tree origin/main aaf1d39f9fd45b8fc39b375e44ab2f0bb4a20acd` exits 0, so there is no conflict (ev/merge-tree.txt).
- Claims and versions: `tests/env_drift.py --claims-only 279578074...` printed `claims hygiene: ... ok`. VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched in the three-dot diff.
- CI at the head (check-runs API, every run listed, ev/checks.txt): every run has concluded, and `gate` has three runs, all success. The only red is `tests / nightly-status`, which grades main's Nightly. The diff does not reach what it reads, and the body's `## Red checks` names it. It is not this pull request's and does not block.
- Packet: no refusals, and figure_lint resolved 12 of 12 figures. The packet advisory `HPO_BUS_TRAIN_STATE is unset` concerns the dispatcher's environment, not this diff.
- Metrics (step 14): the diff moves no budget, closure, claim or score. The body quotes `Architecture score: dS +0.0000 NULL`, which is CI's arch-score, green at this head. I did not re-derive it.
