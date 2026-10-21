Fix review: blocked b18052f664039d36da73ef745a2a8423f82d2c46 vacuous-test: the recorder-reap arm runs closures_line outside a command substitution and without prepr's top-level TERM trap, so deleting the watchdog or the traps leaves it green while production orphans or hangs the recorder

Round 1 (first review of this head). Measured head b18052f664039d36da73ef745a2a8423f82d2c46; it was still the PR head when this was written. Code head 7eee5b39e is byte-identical to it on all five PR files, so the body's measurement at 7eee5b39e carries. Main moved to 5d433771a. `git merge-tree --write-tree origin/main <head>` exits 0 (tree f4b575467), so the merge is clean and no absorb is owed. `fix-review.md` is unchanged on main since the merge base; only orchestrator.md moved.

## Blocking: the second arm (the recorder dies with the prepr) is not pinned

The reap block has two mechanisms: the TERM/INT traps and the `$$` watchdog. The self-test arm "a TERM to the prepr leaves no recorder running behind it" drives `closures_line` directly in `drv.sh`. That is not inside `$(...)`, and the driver evals prepr only up to `rc=0`, so it never sets the slot block's top-level `trap 'exit 143' TERM` (prepr.sh:2683/2692). Production runs `CLOSURES_LINE=$(closures_line "$BASE")` (2922) after that trap is set. So the arm reproduces neither production case.

Step-1 mutants, each a copy of the head's prepr.sh run with `--self-test` under /etc/profile.d/hpo-toolchain.sh (Python 3.14). The head gives 321 passed, 0 failed. M0 (an unmodified copy) gives 320 passed, 1 failed: `a change to prepr.sh owes the self-test`, which is the runner's own failure and is in every row below.
RESULT M1 (delete `return 1` in closures_records_here): 317/4. Killed by the three off-Linux arms (matches the body).
RESULT M2 (delete the PREPR_RECORD_CLOSURES override): 318/3. Killed by the two opt-in arms (matches the body).
RESULT M3setm (delete `set -m`): 319/2. Killed by the reap arm.
RESULT M3trap (delete both `trap 'reap_recorder; ...'` lines): 320/1. SURVIVES. Nothing beyond M0 fails.
RESULT M3wd2 (watchdog body replaced by `( : ) & wpid=$!`): 320/1. SURVIVES. A cruder M3wd that deleted the watchdog line outright failed 6 recording arms through an unset `$wpid`, but the reap arm stayed green.
The body's M3 deletes both mechanisms at once, which hides that each passes alone.

A production-shaped probe (ev/probe.sh) closes that gap. It evals prepr up to `rc=0`, sets the slot block's traps, and calls `X=$(closures_line <base>)` on a clone whose diff touches tests/wood_advisor.py. A sleeper stands in for the recorder, under `setsid`. Each line is the recorder, and the prepr, still alive 5 s after the signal:
RESULT head  KILL->prepr: prepr gone, recorder reaped | base 3688cf2: recorder ORPHANED (the finding's case; the watchdog fixes it)
RESULT head  TERM->pgrp / HUP->pgrp: reaped | base: reaped
RESULT head  TERM->prepr alone: prepr AND recorder alive. The prepr's own trap defers until the recorder finishes (ev/probe-term-deferral.txt: rc 143 at +15 s for a 15 s recorder). Base is the same.
RESULT M3wd/M3wd2 KILL->prepr: recorder ORPHANED. The self-test stays green.
RESULT M3trap TERM->pgrp: prepr AND recorder stay alive. The watchdog subshell holds the `$(...)` pipe open while it waits on `$$`, and `$$` waits on that pipe. This is a hang the traps prevent. The self-test stays green.

So each mechanism is load-bearing in production, and neither is pinned. Also, the arm's name, the code comment at prepr.sh:556-561 ("a TERM to the prepr alone ... still ends the closure work") and the body's "a TERM/INT trap reaps that group" all state a case that the head does not deliver in production. A TERM to the prepr alone is deferred by its own trap, and the recorder runs to completion. What the head delivers is: KILL to the prepr (the watchdog), and TERM or HUP to the process group (the traps). To unblock: drive the arm through `$(closures_line ...)` with prepr's top-level traps installed, and give each mechanism its own arm (KILL the prepr; TERM its group). Then either make a TERM to the prepr alone end the work, or correct the comment, the arm's name and the body to the cases it does cover.

## The rest, which held
- Off-Linux default and opt-in: M1 and M2 kill exactly the arms the body names. The `full` and `skip` lines are pinned byte-identical. Linux behaviour is unchanged (the null-control arm is green at the head).
- Class: tools/pr/prepr.sh has one recorder launch (line 569) and one platform predicate, so the class is one seam. No other seam returned.
- Finder's harness (step 9): the reopened group has no committed harness. Its evidence is the owner ruling plus the roster resume note's 6b-outcome count (108 ok, 13 skip, 3 REFUSE), which is out of tree. I built no instrument of my own beyond ev/probe.sh, which is mine, not the finder's. The body does not carry the roster note's "recommendation on record" (force PREPR_RECORD_CLOSURES=1 on diffs touching tests/closures.json, tests/closure.py or an INERT read). That is not an owner ruling, so it is not a block, but it is undispositioned.
- Figures re-derived at the head (ev/cheap-checks.txt):
  - `RULES-SYNC ok`, and 0 conflict markers in both generated copies.
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, with scope.run = tests/entities.py.
  - `STRUCTURE RATCHET PASSED`, and `claims hygiene: 3688cf2 ok`.
  - The self-test gives 321 passed, 0 failed.
  - VERSION, the manifest, RELEASE_NOTES and tests/golden are untouched. No claim file moved.
- CI at this head (check-runs API, ev/check-runs.tsv): every run concluded. The one red is `nightly-status`, which grades main's scheduled slow run. The diff reaches nothing it reads, and the body answers it. `pr-contract` was green at 13:16:52Z, after the last other run concluded (Analyze (python), 13:15:58Z). The earlier head's red `pr-contract` (carry_audit UNROUTED) is answered in the body, so step 11 holds.
- Policy half: gate-scoping.md and its generated copies still owe tvofi's approving review. That is not mine to give.
- Minor, not blocking: `[ -n "${PREPR_RECORD_CLOSURES:-}" ]` means that `PREPR_RECORD_CLOSURES=0` opts in.

bus-nonce: 6f43192ea7aa130e69cbd1ebe0306a7b
