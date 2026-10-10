Fix review: merge 44b5c3e53295d5875c20d5582f9575398fd391d7

bus-nonce: 1ea087e0b9be00b61bd5977722e2e224

I measured the head named above, in a detached worktree of my own at
/Users/timmalmstrom/hpo-seats/r9rev-2113/wt, against the merge base
7cd5a588cbbbef354c00148040da2d720b8a888c. Evidence bundle:
/Users/timmalmstrom/hpo-seats/r9rev-2113/evidence-2113/ (MEASUREMENTS.md names
this SHA). This is round 1 for this branch; nothing here is a re-review.

== Q1. Does the drop remove the two measured nights without silently losing
   what they drove? ==

The two nights are real and are the ones the body names, and I opened both.

  RESULT run 37108891698 job mutation-ledger (10-03): "MUTATION TABLE REFUSED --
    the null control custom_components/heatpump_optimizer/__init__.py:42
    NULL_COMMENT was killed by tests/harness_headers.py
    (tools/audit/round4/D7/sysid_estimator_frontier.py exits 0 [rc=-24 ...])"
  RESULT run 37189092011 job mutation-ledger (10-04): "... killed by
    tests/stress.py (no scenario exceeds its own recorded cost by the budget
    factor [summer/1z/dhw/fuse-cap at 8.0x its reference vs its own budget
    7.9x (recorded 2.6x x 3)]; ...)"

Both evenings the sibling lane `mutation-nightly` PASSED. So the arm is the
ledger lane and the refusal is load-dependent, not deterministic; the body's
"two-of-six-nights arm" is accurate and the change is the arm's stated form
(#1930 (a)), which tvofi approved verbatim at comment `6078664059`.

The drop does what it says, by the tree's own functions:

  RESULT scope_deferred("full") = ('tests/harness_headers.py', 'tests/stress.py')
  RESULT scope_deferred("changed") = ()
  RESULT files_losing_a_driver_OUTSIDE_the_drop = [] over all 75 production files
  RESULT files_losing_one_at_all = 75 (0 at the merge base)
  RESULT drivers unioned over the tree 26 -> 24; unpinned 4617 of 5983 at both ends

WHAT IS LOST, NAMED. Not nothing, and the body says so in three durable places
(the census clause, the ledger's `reason`, the RCA), so it is not silent:

  - 4 recorded `killed_by` rows lose nightly re-verification -- 3 pinned to
    tests/stress.py (`optimizer.py:HeatPumpOptimizer.get_current_action BOOLOP
    519a7ed9`, `thermal_model.py:ThermalModel.flow_lift_factor CLAMP_DROP
    bc44c8b4`, `thermal_model.py:ThermalModel.simulate_trajectory_batch BOOLOP
    b5554584`) and 1 to tests/harness_headers.py (`quiet_windows.py:overlap_problem
    RETURN_DEL da9e8e97`). My harness returns exactly this set and the count 4,
    and the RCA's four names match it key for key. Two of the four were recorded
    by the nightly's own `--drain` lane -- the lane that loses stress.py.
  - the drain lane loses those two as candidate killers: harness_headers.py's
    closure contains ALL 75 production modules (so it was a candidate driver on
    every site, all 4617 unpinned ones included) and stress.py's contains 23
    (1772 of the 4617). Its power to dispose of the unpinned stock is reduced,
    unquantified by the body and unquantifiable without a nightly.
  - NOT lost: the pull-request gate. `scope_deferred("changed") == ()`, and both
    the pin path (`mutation-pins` drives the base's own `--pin-killed`, default
    scope `changed`) and the `mutation` job (`--scope changed --max 10`) keep
    both drivers. A diff that adds a site they can kill still gets pinned by them.

The cost is small where it can be measured. On the last two green nightly draws
of the very lane that keeps running:

  RESULT 10-03 mutation-nightly, 40 mutants: features.py 23, finite_boundary 5,
    entities 5, manual_plan 1, config_flow_steps 1; 4 survivors of 39 = 10.3%.
  RESULT 10-04: features.py 15, entities 5, finite_boundary 3, structure 1,
    config_flow_steps 1; 7 survivors of 32 = 21.9%, cap 30%.
  Zero kills by either dropped driver, in 72 evaluated mutants. Ledger-wide the
  pair hold 4 of 1260 rows; tests/features.py holds 775.

NOT RE-DERIVED, and I say so rather than confirm it. The body's "the other four
sites LIVES against every remaining driver" is qualified in its own words
("--scripts <every remaining driver green unmutated>"), and the fixer's replay
log at /Users/timmalmstrom/hpo-seats/nightly-defer/logs/replay_tier1.txt excludes
tests/features.py -- the ledger's dominant killer, 775 of 1260 rows -- because
its unmutated run is red on a Mac seat. So the residue is proven against 18 of
the net's drivers, not all of them; features.py might kill one of the four and
offer a re-point. That errs toward MORE owed work than the RCA records, never
less, so it does not change this verdict; I did not spend the ~40 minutes per
anchor to close it.

== Q2. Is the null control driven to completion for every night that still runs? ==

For the pair, yes, by construction and by measurement.

  - In code the drop happens before any pool is drawn: `allow.remove(s)` sits
    right after `allow = [s for s in args.scripts.split(",") if s]`, and every
    pool branch (sampled, `--anchor`, `--drain`, `--pin-killed`) derives each
    mutant's drivers from that `allow`, so `needed` -- which the null control is
    driven over -- cannot contain either. My per-file walk confirms the net
    change on all 75 files and no file loses anything outside the pair.
  - Empirically the pair are the whole class. `setrlimit`/`RLIMIT_CPU` on a child
    appears in exactly one script in the tree (tests/harness_headers.py), and a
    driver comparing a measured duration against its own budget appears in
    exactly one net driver (tests/stress.py); tests/structure.py's mention of
    stress_budgets.json is a docstring about counts, and tests/features.py's
    budget-file hits are fixture paths and comments. On 10-03 the sibling lane
    drove the SAME 22 drivers on the SAME null-control site and printed "null
    control ... survived every driver". So no third machine-measuring driver in
    the net refuses it.
  - The lane still has other refusal arms this pull request does not claim and
    does not close: the measured-pool-cost timeout bound (main's `955dd09a3`)
    and the `max_survivor_fraction["full"]` cap, which 10-04 ran at 21.9%
    against 30%. The drop cannot move either much -- it converts a mutant to a
    survivor only where the pair were the sole killer, which was zero of 72
    draws -- but they are the arms to watch, not this one.

== Q3. Does it stay inside the mutation lane, and does it route this PR serial? ==

  RESULT files changed in the range: dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md,
    dev/programme/delivery/2113.md, tests/entities.py, tests/mutation_budgets.json,
    tests/mutation_ledger/killed_by/boost.py/space_learning_frozen.BOOLOP.ad026ebf.json,
    tests/mutation_table.py
  RESULT .github/workflows/: 0 files touched

It stays inside the mutation lane's own code and its own checks, and it touches
no workflow file, so nothing about it routes the PR serial: no policy file, no
hook, no gate carrier. Its one `*_budgets.json` edit is the appended `reason`
clause, and CI's own gate agrees it is not a raise -- "RESULT budget_raises=0
count / PASS: no budget raise; no owner review is owed" (job 114236486119,
base d3dbf2c3f, head 44b5c3e53) -- so no `budget-raise-gate` review is owed and
no serial admission on a cap. arch-score is flat: "dS +0.0000 NULL, no gate
metric rose".

== The rest of the contract ==

  RESULT mutation proof, through the FULL closure (my own, not the four
    predicates): control ALL 2254 ENTITY CHECKS PASSED; M1 (the drop loop
    deleted from main()) 1 of 2254 FAILED, exactly the named check, the other
    three green; M2 (SCOPE_DEFERRED = {}) 4 of 2254 FAILED with the net walk at
    "26 -> 26" and "files losing one at all=0". Restored to 0 diff lines after
    each; the worktree ended clean. The fixer's own arm could not run this
    (both entities runs were SIGTERM'd, rc=143) and its body says so.
  RESULT claim files byte-identical to the merge base; VERSION 6.7.17, manifest
    6.7.17 and the RELEASE_NOTES heading untouched; merge-tree --write-tree
    exit 0 with no conflicting path and no MERGE-CLAIM marker.
  RESULT red checks: the range pushed none. Only `cancelled` results sit on
    14b891508, superseded by the head's push, and the head's `closures`,
    `fast (3.14)`, `mutation`, `closure-scope`, `pr-contract` and
    `budget-raise-gate` are green. The body answers the two REFUSE lines the
    fixer's own prepr produced (`closures`, `pr-body`); `closures` is answered
    by a re-run I can read ("ALL 109 HARNESS HEADER CHECKS PASSED", rc=0,
    11:51:21Z -> 11:55:59Z) and the head's own `closures` is green.
  RESULT forward-carry: the destination the body names,
    dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md, is in the diff, keeps section
    4(iv) as written, corrects the sign of the cost and the storability of the
    count, and names the four stranded pins as owed work.
  RESULT figure_lint on the live body: "8 resolved, 1 not verified, 0 refused"
    -- the unverified one is the `<merge base>` placeholder in a `git diff`
    invocation, which I closed by hand instead.

== One correction the record should carry (not a block) ==

The body's "`python3 tests/entities.py` -> ALL 2254 ENTITY CHECKS PASSED (was
2243 before this diff)" does not re-derive. I measured both ends with the
fixer's own interpreter and PYTHONPATH:

  RESULT entities.py at the merge base 7cd5a588: ALL 2250 ENTITY CHECKS PASSED
  RESULT entities.py at the head 44b5c3e53:     ALL 2254 ENTITY CHECKS PASSED

so the pre-diff figure under CLAUDE.md rule 3's three-dot rule is 2250, and the
delta is +4, which is exactly the four new arms. The "2243" is the count on the
branch's pre-merge fork tree (2320fa4c4's parent 23d354970), which the merge
e797e30bc superseded; "7" of the head's checks come from main, not from this
diff. The claim the sentence supports ("the four arms are new") is true and
proven by my M1/M2 arms, so I did not route a repair round for a parenthetical
whose class the vocabulary has no word for. Say 2250 if the body is ever re-taken.

Two smaller things for the orchestrator, neither blocking: the branch is 33
commits behind main but main has touched none of the five files it changes
(`git diff <merge base> origin/main` over them is empty), so a main merge
returns as a resolution delta only; and the fixer's second prepr left one
`check` line unanswered -- CLAUDE.md and dev/governance/roles/fixer.md moved on
main since its base while the branch does not touch them, which is a re-read,
not a defect.

== Verdict ==

merge. The change is what its body says, the two nights it removes are real and
were opened, the null control cannot reach either driver afterwards, the class
it defers is the whole class of machine-measuring net drivers, nothing outside
the mutation lane is touched, no cap moved, no claim or version moved, and the
four stranded pins are named in the tree rather than swallowed. I measured this
claim at head 44b5c3e53295d5875c20d5582f9575398fd391d7 and re-checked
`git ls-remote origin refs/heads/fix/r9-nightly-defer` immediately before
publishing: still 44b5c3e53.
