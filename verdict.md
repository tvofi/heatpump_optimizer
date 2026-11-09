Fix review: merge 45ece77a354dc2b1f752ff4cd3d1f0631c49841f

bus-nonce: ec9c0a2df97b30543200fd6088eab1be

Round 1. Measured head 45ece77a354dc2b1f752ff4cd3d1f0631c49841f (the PR head named in the body).

## Findings

none

## Evidence

- RESULT mutation: deleting `'red-checks'` from FRICTION_FAMILIES.root-cause (head's policy_lint.mjs, run as a copy): `--self-test` prints `FIXTURE VACUOUS: ... `red-checks` is a member ...`; unmutated head prints `FIXTURE ok: 93 error(s) hold 269 pins`. The new rcSpelled pin is not vacuous (ev/selftest-mutant.txt, ev/selftest-head.txt).
- RESULT null control: rcNull (detectable+unrecorded alone) is asserted at 2 in the same pin; the mutant fails on rcSpelled's 3, so the pin reads the member.
- RESULT merge: `git merge-tree --write-tree origin/main 45ece77a354dc2b1f752ff4cd3d1f0631c49841f` rc=0, no conflict (ev/merge-tree.txt).
- RESULT untouched: VERSION, RELEASE_NOTES.md, tests/golden: no diff three-dot (ev/untouched.txt); no claim file, budget, closure or INERT movement; the diff is one list entry, one assertion, a record and a delivery row. Role contracts: no drift between merge base and main.
- Class (step 6): the issue (#3283) states one seam, the `red-checks` spelling; the body names no multi-seam rule. The declared root-cause family's other members are already present. One seam, nothing open.
- Figures: the body's stats figures are window-dependent and it says so. At my checkout (tag v7.1.8 present) `--stats --since v7.1.5` prints `root-cause (family)` 2 / 3 and `other (untaught)` 9 / 11, not the body's 1 / 2 and 6 / 7: the window has moved since the base, so I could not re-derive those at the body's main. The direction claimed (a root-cause family row appears, untaught stays over threshold) holds. Entry counts for class-open and mutation-vacuous are the cache read and I did not re-read them; the record says so under "Not established".
- CI: packet digest lists pr-contract, budget-raise-gate, arch-score, tests/* green; `governance / delivery-status` red is main's overdue rows, not this diff's (no plan, HANDOVER or row it did not add touched). `merge_train.py classify` exits 1: `RED 45ece77a354dc2b1f752ff4cd3d1f0631c49841f pending: none red: gate` (ev/classify.txt). Cause: `latest_runs` keeps the worst gate suite, and the red one is job 128930883806 of run 42544253425 (KIND=edit), whose log is `FAIL run(s) [42544252871, 42546064085] at this head are still being judged; their gate decides`. Both deferred-to runs' gates concluded success (128941676722 at 02:11Z, 128942144406 at 02:12Z). So the red is a stale deferral, the shape R10-HOTFIX-TRAIN-DEFER-WAIT describes, not a failed check; I judge the head GREEN on that reading but the classifier does not, so the orchestrator should re-run classify or the sweep before the train relies on it. Not a root-cause trigger for the body (no defect behind it).
- Body's `## Red checks: none` accepted on that basis; Forward-carry and Friction none. The PR is a draft and the body says approval is owed from the owner on a policy-adjacent file.
- Not done: no finder's harness exists for #3283 (the packet names none); the instrument is policy_lint --self-test, run by me at head and mutant. I did not re-run the gate or mutation table (cited CI).
