Fix review: merge cd5693f4dfde160c2a1d61ce9557027b64e91bc1

bus-nonce: 61c962e272fb4ceb9039ac611fbc455a

## Round

Round 1 (first fix review of #2913, R10-CONFIGFLOW-PAGES arm B, D7-s2-55). Head measured: `cd5693f4dfde160c2a1d61ce9557027b64e91bc1`, detached worktree. Roles diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read is current.

## Findings

- Pre-existing pin gap, not introduced here: the "never defaults it" half of `_suggested_optional`'s rule is unpinned. Mutant `vol.Optional(key, description={"suggested_value": current[key]})` -> `vol.Optional(key, default=current[key])` survives `tests/config_flow_steps.py` (ALL 505 checks PASSED) at this head, and the same mutant applied to both old helpers survives at base `b0b2d7697` too (ev/mutants.txt, ev/mutants2.txt). It is the voluptuous-refill behaviour that #1258 and the docstring name. Behaviour-neutral hygiene does not owe it here. The group's later arms touch the same sites, so its test should land there. Carry: R10-CONFIGFLOW-PAGES

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main cd5693f4d` exits 0 (tree d5f358be6), with origin/main = b0b2d7697 = the PR's base. No conflict, and no claim-file driver ran.
- RESULT tests/config_flow_steps.py at head: ALL 505 checks PASSED. At base b0b2d7697: ALL 505 checks PASSED. Same count at both ends, as the body's null control states. Run under a local py3.11 venv with requirements-ci's packages installed unpinned, because the seat venv the prompt names was not on PATH in this container. Results are in ev/mutants.txt.
- RESULT mutation proof (re-run by me on `_suggested_optional`): `if key in current:` -> `if False:` gives 1 of 505 FAILED (quick_setup wood_tank_top/bottom lose their suggestion), which matches the body. `return vol.Optional(key)` -> `pass` (the ledger's RETURN_DEL fcaa22f1) gives 6 of 505 FAILED. `if True:` gives rc=1 (KeyError). `vol.Optional` -> `vol.Required` on the fall-through gives rc=1. Every mutant was restored, and `git status` is clean afterwards.
- Ledger: the two killed_by rows collapse into `_suggested_optional.RETURN_DEL.fcaa22f1.json`. The anchor is the same `return vol.Optional(key)` line, and my RETURN_DEL re-run kills it, so the re-key is earned.
- RESULT archscore: at the authored head ad4dd15a5, `score.py --diff 6d86acc90` reads `dS +0.3628 IMPROVES`, `duplication_copies 35 -> 34`, which matches the body and the design's arm-B row. At cd5693f4d the same command reads +0.3640, because the merged main brings `coord_footprint 2410 -> 2408 +0.0012`. That is not this PR's.
- Metric earned (step 14): the duplication_copies drop (budget 15 -> 14) comes from deleting one of two identical helper bodies, a real collapse of one rule's two copies. `tests/structure.py` at head: STRUCTURE RATCHET PASSED. The budget moves down only; no raise.
- Class (step 6): `git grep -n '_options_suggested_numeric\|_suggested_entity\b' -- custom_components` is empty at head (rc=1). The other `suggested_value` sites in config_flow.py (1206, 1815, 1823, 1832, 1956, 2848, 2946) carry different values (a computed suggestion, a fallback, or a mode boolean), not `current[key]` behind a `key in current` guard. They are not copies of this rule, so the class is the two helpers.
- Untouched (step 5): VERSION, RELEASE_NOTES.md, manifest.json and both claim files show 0 paths in the three-dot diff. No golden moved, so there is no drift to claim (step 4).
- Finder's harness (step 2): `run_findings.sh 04_suggested` was not re-run by me. Its figure (`delta_S=+0.1880`, `perturbed_delta_S=+0.0000`) is quoted from the body and from #2238, so I have not verified it. archscore at the head shows the same direction on the same metric.
- Head (step 7): the body's `## Head` names cd5693f4d. The code diff from ad4dd15a5 to this head is the main merges plus the delivery row only.
- Forward-carry (step 10): `dr1-b-c2-conflict` is stated in the approved design note `design/R10-CONFIGFLOW-PAGES` 32892dc67 (lines 69 and 161), with its control: arm C2's fixer applies `_suggested_optional(current, K): <widget>(K)` and re-runs `wizard_widgets.py --all` plus the `_field_marker` and quick-setup tests. That note becomes the group's architect note (roster carry[4]). The body says the carry "lands in" `wave-r10-groups.json`, but no string there names it yet at origin/main. carry_audit reports it routed (1 routed, 0 unrouted).
- CI on cd5693f4d (check-runs API, read at review time): nothing red. Green: arch-score, budget-raise-gate, mutation, closure-scope, typing, arch-instrument, browser, briefs, hassfest, validate-hacs, policy-docs, delivery-status, env-matrix, wave-script, nightly-status, both codeql analyses for actions and JS. Still in progress when I read them: tests/fast (3.14), tests/closures, tests/coverage, codeql python, governance/instrument-self-tests, prelude. With no red check there is no step-11 trigger. The merge train must still see those concluded green.
- Architecture (step 15): one helper in the owning config_flow seam, at three call sites, with the argument order unified to `(current, key)`. No hunk falls outside the architect note's seam.
