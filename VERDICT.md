Fix review: blocked 9512e2090644a7134ebc82818bece5428af73031 harness: class-open tests/rolling.py

bus-nonce: 8bc21cffee263e2a0ac8af0e973e1050

Round 1. Measured and posted at `9512e2090644a7134ebc82818bece5428af73031`; the head has not moved (`git ls-remote refs/heads/fix/r10-prepr-cap-pr` and `refs/pull/2341/head`, `gh pr view 2341`, and a detached worktree at the merge base `81ae048e8bbdf2335fe2016e987ec2739481f293`). My contract copy is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. `git merge-tree --write-tree origin/main HEAD` exits 0, so `mergeStateStatus: BLOCKED` is not a conflict.

Everything below was re-run by me at the head. One open seam blocks it; nothing else is in doubt.

## The instruments I used, and whose they are

The finding's committed instrument is `tools/audit/seat/orchestrator_tick.py` — it counts `prepr.sh` PROCESSES (`orchestrator_tick.py:391`). It measures no cost and the pool did not exist when the finding was taken. No harness for the class is in the tree: the fixer's three probes (`slot_evidence.py`, `slots5.py`, `pgmeasure.py`) live under a scratch directory that a reboot has since emptied, and the fixer disclosed them as their own. So `slot_probe.py` and `prepr_probe.py` in this verdict's evidence directory are **mine, built for this review, and disclosed as mine** (`fix-review.md` step 9). They drive the head's own `gate_lock.py` and `prepr.sh` CLIs, never the fixer's probes.

## Why `harness: class-open tests/rolling.py`

The body names the class rule: "a script that MEASURES the machine takes the exclusive lease (`stress.py`, `harness_headers.py`); one that is multi-minute CPU-bound joins the four slots (a `closures.json` recording at or above `SLOT_MIN_SECONDS`); one that takes seconds runs unleased." That is a partition, and the finding was demonstrated with an instance (the 22:57 tick), so `fixer.md` step 8 binds: the rule run as a command, every seam it returns listed against a disposition. `## Figures` lists probes; no enumeration of the class against dispositions is in the body.

Run as a command over the population of scripts `tests/run.sh` dispatches through `leased` (36), it returns three that carry no recording, of which one is the class the rule names:

    RESULT needs-lease tests/rolling.py (run.sh:619, unrecorded, ~15 min)     -> none
    RESULT needs-lease tests/setup_qa_render.mjs (run.sh:633, unrecorded)     -> none
    RESULT needs-lease tests/closure.py (run.sh:480, unrecorded)              -> none
    RESULT needs-lease tests/nope_not_recorded.py (unknown)                   -> none

`tests/rolling.py` is "the closed-loop simulation runs hundreds of solves and takes about a quarter of an hour" in `tests/run.sh`'s own comment (run.sh:613-619), dispatched through `run` -> `run_always` -> `leased` (run.sh:351), so `needs_lease` decides it; it answers `none`, and it runs unleased. By the body's own rule it is the multi-minute CPU side and joins the pool. `tests/closure.py` is documented "Cheap, no recording" at run.sh:478 and is correctly `none`; the seam is the other two.

The seam is the size of the gap between the rule as written and the rule as implemented, and the code states the wrong side of it. `needs_lease`'s own docstring, on the added lines:

> Fail closed: a scope this cannot classify -- a recording table it cannot read, or a name it does not know -- is leased rather than left unleased, so the unclassified case costs serialisation and never concurrency.

The first clause is implemented (`return "lease"` on an unreadable table). The second is not: an unrecorded name falls through the `>= SLOT_MIN_SECONDS` test to `return "none"` — measured above. The check the fixer added (`entities.py:_gl_auto_lease`) drives `("", stress, entities, structure)` and no unrecorded name, so it pins the three-word classifier and not the docstring's claim; a reader told "an unknown script is leased" will add a heavy script to run.sh and expect it bound, and it will not be.

Either reading gives the same repair, which is cheap: make the code answer the docstring (an unrecorded name joins the pool or takes the lease) and drive it from `_gl_auto_lease`, or narrow the docstring to the recordings-keyed rule and disposition `tests/rolling.py` and `tests/setup_qa_render.mjs` in `## Figures` as out of the class, with the reason.

## What the fix does earn — all re-derived

    # step 1, the mutation proof, at the head (worktree per mutant, `git checkout --` restore)
    RESULT MUT-E1 2 of 2333 ENTITY CHECKS FAILED
      FAIL run.sh leases a FULL or stress run itself, for the scripts that measure alone, and a second one waits  [need=['lease', 'lease', 'none', 'none'] waited=True rc=[3] released=True; ...]
      FAIL the heavy-slot capacity is the cap unless the owner raises it (#2267)  [heavy_slots over (unset,3,8,8+owner,junk,0)=[4, 3, 8, 8, 4, 4]]
    RESULT MUT-E2 2 of 2333 ENTITY CHECKS FAILED
      FAIL run.sh leases a FULL or stress run itself, ...  [need=['lease', 'lease', 'slot', 'none'] ...]
      FAIL derive_closures.sh takes a heavy slot standalone and joins one it is inside (#2267)  [inside_takes=True outside_takes=True]
    RESULT MUT-E3 1 of 2333 ENTITY CHECKS FAILED
      FAIL a heavy slot whose owner process is gone is reclaimed; a live owner's is not (#2267)  [stolen=False live_admitted=False]
    RESULT MUT-P1 273 passed, 1 failed
      FAIL and exports its label, so a nested heavy step joins this slot (got 0, wanted 1)

Four mutants, four reproductions, detail strings character-for-character with the body, and no check beyond the named ones moved. Head baseline beside them: `ALL 2333 ENTITY CHECKS PASSED`.

    # step 2 and 8, the pool's capacity and its queue, my probe against the head's CLI
    RESULT CAPACITY slots=4 n=5: acquired=4 refused=1
    RESULT CAPACITY null control slots=6 n=5: acquired=5 refused=0
    RESULT CAPACITY null control slots=1 n=2: acquired=1 refused=1
    RESULT QUEUE waiting=True rc=0 queued_line=True
    RESULT QUEUE status=.../l4/slots: 4/4 slots held [0:hold3(live), ...] queue=fifth

The body's `acquired=4 refused=1` and its `acquired=5` null are re-derived; the `slots=1` arm is mine and shows the number is the pool's parameter and not a hard-coded four.

    # step 2, both ends against the pre-fix tree
    RESULT CAPACITY slots=4 n=5: acquired=0 refused=5     (origin/main's gate_lock.py has no slot-take subcommand)
    RESULT COST argv=tools/pr/prepr.sh --self-test rc=0 wall=88.8s peak_pg_procs=11 samples=392   (base 81ae048e, 267 passed 0 failed)
    RESULT COST argv=tools/pr/prepr.sh --self-test rc=0 wall=79.7s peak_pg_procs=11 samples=356   (head, 274 passed 0 failed)

Both ends: the nested chain's process count is 11 at the base and 11 at the head, and the head's wall is not higher. The fix adds no cost to a lone run; the cost it adds is the wait a fifth one pays, which is the mechanism.

    # step 3, the null control, reproduced
    RESULT COST argv=tools/pr/prepr.sh /tmp/rev-null-body.md rc=2 wall=0.2s peak_pg_procs=2 samples=1

    # step 14, the bound is earned by the change
    RESULT R4 RECLAIM dead-owner slot stolen by next take: rc=0 ; live-owner slot refused to next take: rc=1
    RESULT BLOCK (head, 4 slots held) while-pool-full reached_step2=False after=75.0s; tail="ok transport"
    RESULT BLOCK (head, 4 slots held) after_release reached_step2=True
    RESULT BLOCK (take removed, 4 slots held) while-pool-full reached_step2=True; tail="ok gate mode  MODE: FULL"

With all four slots held, a real `prepr.sh` at the head stops after `transport` — exactly where step 1b sits — and prints no step-2 `MODE:` line for 75 s, then proceeds within seconds of a slot freeing. With the take removed from the same file, the same run walks straight through to `MODE: FULL` while all four slots are held. The movement does not survive removing the mechanism, so the concurrency bound is the change's and not the instrument's. (My first attempt at this null used a body directly in a temp root and refused at step 1 for that reason; the arm above uses the `<scratch>/<seat>/` path the check accepts.)

## A number I could not re-derive

The body's cost figure, `wall=182.8s peak_pg_procs=11 samples=756`, I re-derived only in part: **peak 11 procs and the 0.2 s / 2-proc null reproduce; 182.8 s does not** (79.7 s at the head, 88.8 s at the base, back to back on a box whose 15-minute load was still falling from my own three entity runs). I did not chase the cause further, so I am not calling it a defect: the figure is load-dependent by construction, the fixer's own note says the box's other seats move it, and the direction of the gap (their number higher, on a box carrying the load the finding is about) is what that account predicts. Treat 182.8 s as an upper bound measured under load, not the chain's intrinsic cost.

One measurement of my own, on the class the cap now binds: a real `prepr.sh` run at the head — the one that refused only at the body step, `MODE: FULL` because a detached HEAD cannot be scoped — peaked at **68 processes in its own process group over 326 s**, not 11. Eleven is the `--self-test` chain alone; the run that holds a slot carries the whole gate. Four slots bound that at four such runs, which is the load the tick saw at 22:57.

## Steps that passed, and where the answers are

- **Claim files (step 4).** `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to the merge base, no fixture moved, and `python3 tests/env_drift.py --claims-only 81ae048e` prints `claims hygiene: 81ae048e... ok`. Nothing is both claimed and may-drift, because nothing moved.
- **Version (step 5).** `VERSION`, the manifest version and the release-notes heading are untouched; the diff carries no `*_budgets.json` and no `dev/governance/config/policy_budgets.json`, so no ratchet was raised. `gate-scoping.md` runs 61 lines at the base to 60 at the head; `nudge.md` 115 to 115.
- **The policy edit is the scope statement, not a re-draft.** The lease paragraph gains exactly the two leases, the three answers, the pool, `$HPO_HEAVY_SLOTS` and `$HPO_SLOT_LABEL`, and that the lease is nudge.md §8's cap. The sentences it drops are relocated and I checked the destinations: first-come-first-served and expiry are in `gate_lock.py`'s module docstring, and "a label that holds no lease fails at once" in `flock_wrap`'s, which is what the body's `## Friction` claims. `rules_sync.mjs --check` prints `RULES-SYNC ok`, `policy_lint.mjs` prints `TOTAL: 0 error(s) across 41 policy file(s)`, and the `.claude/rules/` and `.cursor/rules/` copies in the diff are the generated form. One nit for the owner's read: the shallow-clone paragraph was compressed to buy the room and lost the verb "fetch first" (#1699's remedy), which `git grep` finds nowhere else in the tree. The rest of that paragraph's facts survive.
- **Red checks (step 11).** The head's runs are all success or skipped (`commits/9512e209.../check-runs`) and so are the authored code head's (`f36c16eeb`); that head's twelve `cancelled` runs are the push that superseded it, re-run green at the head. The body's `## Red checks: none` is accurate and no answer is owed. The `mutation` lane's green is vacuous on this diff — its own log prints `scope changed: no production code line added or modified against the base` / `MUTATION TABLE PASSED (empty scope)`, since `tests/mutation_table.py`'s `PRODUCTION` is `custom_components/` and this diff is instrument code — and the body claims nothing of it, resting on the four mutants I re-ran.
- **Forward-carry (step 10).** The body says `none` and names the one observation (the tick counts a waiting fifth as a runner). I checked the destination question and agree it does not meet `finding-propagation.md`'s bar: it narrows no later stage, invalidates no figure a stage is scored against, and removes no option — the tick's advice stays on the conservative side. The seam this verdict blocks on is the class question that observation is not.
- **Soundness (step 15).** The pool reuses the single lease's `Owner`/ticket/expiry/`_steal`/`_read_at` primitives rather than forking them, its own lock directory keeps the two resources' FIFOs apart, and `set -u` safety holds at both shell call sites (`${HPO_SLOT_LABEL:-}`). CI's `arch-score`, `budget-raise-gate`, `pr-contract` and `instrument-self-tests` all concluded success at the head. **`## Approval` is right to owe tvofi's approving review**: the diff is code-owned through `dev/governance/rules/gate-scoping.md` and `dev/governance/roles/nudge.md`, and the roster's `owner_gate: null` is stale.

## What is owed

One repair, one re-review. `## Figures` gains the enumeration of the class (`tests/rolling.py`, `tests/setup_qa_render.mjs`, `tests/closure.py` unrecorded, each with its disposition), and `needs_lease` and its docstring agree — code follows the fail-closed sentence, or the sentence follows the code. Evidence for this verdict, including the three mutant logs, the four probes and their raw output, is the directory beside it; every RESULT above is in it.
