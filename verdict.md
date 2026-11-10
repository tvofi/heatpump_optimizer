Fix review: blocked b9ec7037e186cac00c9b57fc9d0099fd08ddf4f5 carry-missing: R10-PREPR-RESIDUE carries 8-11 hold the claims without their controls

bus-nonce: 43dea72004e3d7eaebb6cb0e7deaef6e

Round 1. Reviewed at head b9ec7037e186cac00c9b57fc9d0099fd08ddf4f5 (merge base 0362916ac7, measurements at b0762725099f). The PR body's head and code head match the commits (`572355a9b` merges main into `6839549f`; `b9ec7037` adds only `dev/programme/delivery/3411.md`).

## Block

- fix-review.md step 10 requires the reviewer to open the forward-carry and confirm it states its control as a precondition (finding-propagation.md, "Carry the control, not only the claim"). The four carries are on `origin/handoff/audit-r10-roster` at `1b225f721` (added by `8ad73ff72`), in `wave-r10-groups.json`, group R10-PREPR-RESIDUE, carry entries 8 to 11. Each one is a copy of a one-line `## Forward-carry` body item and states no control:
  - 8 (C1) says the receipt is carried "from the parent body tip or onto a descendant code head" and that `reuse_verdict` re-proves it. It leaves out the null control from RCA section 6: a non-merge commit past the receipt keeps the trailer and gets `reuse_verdict` rc 1. It also leaves out the non-ancestor case, where no trailer is written.
  - 9 (C2) and 10 (C3) name no failing-then-passing case.
  - 11 (C4) leaves out the proof that section 6 names: 6d's wall time on `6671786843` before and after, with the same PREDICT lines both times.
  - No entry cites `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md`, and the group's `rca` field is `[]`. The group's own brief says "Each carry states its failing test and null control", and these four do not. A fixer dispatched from the roster gets C1 without the case that keeps it from skipping prepr on unproved code.
  - Remedy, one `roster_edit.py append-carry` (or an edit to 8-11): name the RCA path and section 6, and state each arm's failing case and null control as a precondition.
- The same record also omits the citation that defect-root-cause.md's "Where it is recorded" requires: the analysis is "`dev/audit/rca/<id>.md`, cited by `rca` in `bugclasses.json`". This PR adds no `dev/audit/config/bugclasses.json` entry. The sibling RCAs R10-RCA-RELAY-HANDOFF-STARVATION (`859a6264e`) and R10-RCA-CLOSURE-ARGV (`80cf79c2c`) each added theirs in the same commit as the document. That entry is where the process states, (c) for C-A and (d) for C-B, and the proposed countermeasures become readable by `fold_ledger.py`. Add it in this PR.

## Findings

- Follow-up: the 49 "never" handoff-body tips, the three instances that triggered this RCA among them, have no established process state. C2 is the instrument meant to split them. Until it lands, the triggering instances are explained by C-B only, and C-A's (c) rests on the 29-tip class, not on the instances. Carry: R10-PREPR-RESIDUE
- Follow-up: the local-host figures (load, swap, CPU-loop multipliers, slot `taken_at`, `p1.log` medians 17/1 min with n=63/59, 509/6 self-test result) are cited from out-of-tree scratch `~/hpo-seats/r10s6/rca-slow-prepr/`. No reviewer can re-derive them, and they will be gone when the host's scratch is cleaned. The `p1-durations.txt` table carries the cost test, and it should land beside the document, as `relay_handoff_lag.py` did for #3352. Carry: R10-PREPR-RESIDUE

## Evidence

- Merges cleanly: `git merge-tree --write-tree origin/main b9ec7037` rc=0 against origin/main 734b806ac (`ev/merge-tree.txt`).
- Diff: 2 files, both new: `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md` (225 lines) and `dev/programme/delivery/3411.md`. VERSION, the manifest version and the RELEASE_NOTES heading are untouched. There are no claim files and no budgets, so there is no mutation proof to re-run and no countermeasure lands (body: n/a).
- Root-cause contract (root-cause.md):
  - Cause: named, two causes (C-A, C-B).
  - C-A reproduced from the code at b0762725:
    - `body_push.sh` `prepr_trailer` writes `Prepr:` only when the local receipt's sha equals the code head (`[ "$s" = "$2" ]`).
    - `app_push.sh` `reuse_verdict` accepts any receipted code that is an ancestor of HEAD, provided HEAD is the clean merge of it with main (`ev/receipt-code.txt`).
    - The asymmetry is real, so (c) is shown with the process quoted, not (b).
  - C-B as (d): the 4-slot cap is unchanged since `c09cf1201024` (2026-10-16, "make the four-prepr cap a lease"), `HEAVY_SLOTS = 4` both there (line 73) and at the base (line 103). It is not recorded as (b), and no firmer-instruction countermeasure is proposed.
  - Reach search: present (handoff-body class table).
  - Cost test: has numbers.
  - Refusal: recorded, for the HEAVY_SLOTS change.
- Figures re-derived at b0762725 (`ev/figures-git.txt`):
  - prepr.sh is 2734 lines with 123 `^ *st ` sites at c09cf12010, and 4682 lines with 325 sites at the base.
  - `grep -rnE 'timeout (3000|7200)' tools/ dev/governance/ .claude/` prints nothing.
  - The 6d comment says "so it costs seconds" (prepr.sh:595).
  - ci_predict.py:45 says "GRADER, minutes where keyed".
  - The named failing tests are at prepr.sh:3067 and :3770, and the third is at :3772.
  - All as stated.
- Handoff-body class, re-derived with my own definition (`ev/handoff-body-rederive.txt`, script `hb.py`):
  - Tips committed 2026-11-06T00Z to 2026-11-10T03:30Z that have not moved since: 10 refs have a tip after 03:30Z, so the 03:30Z snapshot is not exactly recoverable.
  - Counts: 12 result bodies, 57 with a trailer, 81 without, 138 code bodies, against 12/60/82/142 claimed.
  - Split: 5 same, 25 merge-only ancestor, 2 new non-merge, 49 never, against 5/24/4/49.
  - merge-tree tree-equal for 25 of 27, against 29 of 33.
  - Consistent with the claim within the moved refs. The exact figures are not re-derivable.
- Not re-derivable here (out-of-tree, local host): every `ps`/`sysctl`/`vm_stat`/`iostat` reading, slot times, `p1.log` durations and medians, the CPU-loop null control, and the 509/6 self-test result.
- CI run 42577505324 is the Governance run, scheduled on main, 2026-11-09 07:09Z to 07:38Z. The 14.0 min job figure itself was not read.
- carry_audit at the head: 4 routed, 0 unrouted, 0 bad. Routing exists; controls are absent (Block).
- Required set: `merge_train.py owed-reds` (`ev/owed-reds.txt`).
- CI: `merge_train.py classify b9ec7037 --pr 3411` printed `GREEN b9ec7037e186cac00c9b57fc9d0099fd08ddf4f5 pending: none red: none` and exited 0 at 07:55:22Z (`ev/classify.txt`). No required check went red, so no `## Red checks` answer is owed. The block above is not about CI.
