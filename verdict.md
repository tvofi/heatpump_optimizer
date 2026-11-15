Fix review: blocked 03c8a591847756bb3ef47cc11693638602e026ba ci-red: governance / policy-docs whole-corpus budget about 69836 tokens over the 69833 cap against current main, from this PR's +96

bus-nonce: 8ce6d3212c3c08de537363a7f3515ed1

## Block

- Round 1 (first review of this PR; review scope full).
- `governance / policy-docs` (a required check named by `merge_train.py owed-reds`) concluded failure at this head, job 132955037797: `ERROR [budgets] (whole corpus): about 69836 tokens exceeds the cap of 69833`. CI grades the PR's merge with current main (GOLDEN_REF 98847b99d7bb). I reproduced it on `git merge-tree --write-tree origin/main 03c8a591847756bb3ef47cc11693638602e026ba` (tree 21560f7834399e114b363601704613fa21a3af8b), which reports `corpus: ~69836 tokens, cap 69333 +band 500 = 69833`. The PR alone measures 69077 -> 69173 (+96) against its merge base 66865be375. origin/main 98847b99d7 alone measures 69740 and passes. So this PR's own growth puts the merge 3 tokens over the cap. The train re-proves on current main and would fail the same way, and a `merge` verdict over this red would be refused (C8). The fix is the body's stated rule: pay the 96 tokens inside the corpus cap by cutting text, or raise the cap deliberately under `ratchet-budgets.md`.
- `tests / fast (3.14)` and `gate` also concluded failure at this head. The fast job reports `1 TEST SCRIPT(S) FAILED` in a lane that ran `tests/entities.py`. The body records that entities' template arm keys on policy_lint's exit code. That makes the same budget red its likely cause, but I did not re-run entities on the merged tree, so this attribution is not verified.
- `merge_train.py classify 03c8a591847756bb3ef47cc11693638602e026ba --pr 3626` last exited 2 (unreadable): `REFUSE selftests: the base's governance / instrument-self-tests job 132905064799 is cancelled, which reads no step: an introduced red cannot be ruled out (fail closed)`. The head's `governance / instrument-self-tests` job 132955037899 concluded failure. Whether that red is introduced here or inherited from main is unreadable from this seat.

## Evidence

- Head reviewed: 03c8a591847756bb3ef47cc11693638602e026ba (the PR's head as read, and the body's `## Head`). Merge base 66865be375f4ee283ee556f53fcd76cc3dbf40e2. `git merge-tree --write-tree origin/main <head>` exit 0, no conflict.
- `dev/governance/roles/` is unchanged between the merge base and origin/main, so the contract is current.
- RESULT hooks_setup self-test at head (`TMPDIR` on a non-symlinked directory): `hooks_setup self-test: 74 checks, 0 failed`. That run includes the PR's 8 new MUTANTS, each red (ev/selftest-head.txt).
- RESULT own mutant `gone = []` (removed pages never listed): `51 checks, 2 failed`, killed (ev/mutant-gone-empty.txt).
- RESULT own mutant proof manifest records only BY_CHANGE blobs: `51 checks, 1 failed`, killed (ev/mutant-manifest-rest-only.txt).
- Null controls: the self-test's nothing-changed, no-manifest and un-mutated cases are green at head, as stated.
- Figures re-derived at head: `STRUCTURE RATCHET PASSED`. `TOTAL: 0 error(s) across 52 policy file(s)` and `FIXTURE ok: 93 error(s) hold 276 pins across 12 check classes` (on the head alone; red on the merge, see Block). Budgets `CLAUDE.md 214 221 3605 3605`, `fixer.md 315 315 5210 5216`, `orchestrator.md 294 295 4250 4251`, `proposal-triage.md 38 40 538 563`, `always-loaded: ~3605 tokens`. `layout: GUARD: 0 refusal(s) against 66865be375f4`. `SELF-TEST passed (every perturbed scope refused)`. `ok coverage tracked=11270 in_universe=1609 excluded=9661 unclassified=0`.
- Not re-derived: the entities count 2723 and the env-matrix `16 declared outcome(s) held`; I did not run them.
- No change to VERSION, the manifest, the RELEASE_NOTES heading, `custom_components/` or any golden or claim file, so steps 4 and 5 hold trivially.
- Finder's harness: none named; this is a policy and instrument PR with no audit finding. The hook's self-test is the fixer's own instrument.
- CI state: ev/ci-reds.txt and ev/classify.log. Corpus measurements: ev/corpus-budget.txt.
- Grepped `dev/programme/RULINGS.md` for opinion wording (`opinion|I think|I feel|annoy|frustrat|happy|angry|disappoint`): no hit. The body discloses that the entries were not re-screened against the new CLAUDE.md section.
- The forward-carry group R11-INTAKE-R10-RESIDUE exists on main. I did not open its brief to confirm that the carried control is stated there.

## Notes

- Note: figure: the body quotes `corpus: ~69190 tokens`, but this seat measures ~69173 at both 5889afaea6 and the head, and ~69836 on the merge with current main. The body's "No cap changes" is only true against the merge base.
