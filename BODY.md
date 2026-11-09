R10-BODY-CONTRACT part 3 (card 7, option B, registry blocks). `pr-contract` renders a figure block only from an instrument that `tools/pr/figure_registry.json` names in the BASE tree, and the body quotes it verbatim; the author chooses no command. Only registered figures are structurally non-stale.

New files: `tools/pr/figure_block.py` (renderer, refresh, verify, self-test), `tools/pr/figure_registry.json` (scope-line, structure-ratchet, merge-base), `tools/audit/seat/instruments/figure_block.py.md`. Option A refused (figure_lint reason 4 stands, header narrowed), option C is the writer (`body_push.sh` runs `figure_block.py refresh`; `prepr.sh` verifies, including the body-only path), `pr-contract` only verifies.

Legacy control (second item): dismissed citing `LEGACY_CONTROL_CAP` and `assertLegacyControl`; re-measured at the merge base, every member of `LEGACY_CONTROL_FILES` still draws a control error with the exemption removed (scratch driver calling `lintCarryFile` with an empty set), so none is dropped.

Carry dispositions (the packet's 1-based numbering; the brief's 0-based index plus one):

Carry 1 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 2 - answered by the card 7 build (option B).
Carry 3 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 4 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 5 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 6 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 7 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 8 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 9 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 10 - already built at the base: `body_push.sh` keeps a refused body on `handoff-wip/<topic>-body` (8a2492ab5, on origin/main); this handoff's first body push printed `body_push: refused body kept at handoff-wip/r10-body-contract-p3-body`, so part 3 has nothing to build for it.
Carry 11 - answered by the card 7 build (option B).
Carry 12 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 13 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 14 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 15 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 16 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 17 - answered by the card 7 build (option B).
Carry 18 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 19 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 20 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 21 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 22 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 23 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 24 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 25 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 26 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 27 - answered by the card 7 build (option B).
Carry 28 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 29 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 30 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 31 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 32 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 33 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 34 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 35 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 36 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 37 - answered by the card 7 build (option B).
Carry 38 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 39 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 40 - answered by the card 7 build (option B).
Carry 41 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 42 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.

Carry 43 - built here (card 7 ruling; roster index 42, 0-based).
Carry 44 - built by #3318 (the group's part 4: `carry_audit.landed()` reads an own-group carry status as a status line), as carry 47 records.
Carry 45 - status line from #3318 (item 52b55967) on carry 9 (#2438): already built at the base (a17d51d41, #3260, fde0de40f), as that body says; nothing for part 3.
Carry 46 - status line from #3318 (item fe95bcab) on carry 10: answered above, already built at the base by 8a2492ab5.
Carry 47 - status line from #3318 (item 4a5f7e3c) on carry 44: built by #3318; nothing for part 3.
Carry 48 - held by the group's other part (carry_audit continuation and quoted-phrase parsing); part 3 takes card 7 and its legacy-control item only.
Carry 49 - held by the group's other part (part 5: carry_audit NONBLOCK section scoping, triage batch 137 P440, built together with carry 47); part 3 takes card 7 and its legacy-control item only.

Earlier repair round (head 86f9e729f, unchanged here): `figure_block.py`'s self-test repository is built through `tests/throwaway_git.py` (`throwaway_git_init`), which clears the prepr self-test's two `throwaway_git.py --check` failures; the `field_coverage.mjs` entry for `pinned tools/pr/figure_block.py` is in its final shape (`none:`, no `pending:`).

Merge round (this push): the bootstrap #3312 (859434ba16) landed the same entry on main with `pending: 'R10-BODY-CONTRACT part 3 pins it in governance.yml'`, so merging origin/main conflicted on that one line of the DECLARED registry. Resolved by taking this head's entry (no `pending:`). The bootstrap's `field_coverage.mjs` hunk, three-dot from the old merge base to origin/main, was that one added line and nothing else, so no other main-side change to the file exists to lose; the merged file is byte-identical to the tip's (`git diff HEAD -- tools/policy/field_coverage.mjs` empty before the merge commit). `tests/closures.json` auto-resolved through LEDGER-MERGE (`closures.tests/entities.py` merged as a set); its diff against origin/main is exactly this branch's two added members, `tools/pr/figure_block.py` and `tools/pr/figure_registry.json`. Because the base now carries the pending entry, the former `governance / policy-docs` red (the base's copy refusing an unregistered pin) no longer applies.

The pin is double: `codeowners_gap.py` derives `PINNED tools/pr/figure_block.py` from both `.github/workflows/governance.yml` (step `Show the figure-block renderer refusing its own fixtures`, `--self-test`) and `.github/workflows/pr-contract.yml` (`figure_block.py verify`). The brief's null control (delete the governance.yml step alone) therefore does not move field_coverage; it is reported below as measured, and the null control that does move it removes both.

Step ref: the previous seat's `handoff-wip/r10-body-contract-p3` tip held only a BLOCKED.md note on 86f9e729f; it was advanced fast-forward by a tree-preserving wrapper commit, and that note is not in the code head.

## Head

fcd03452c746d9f61fb4aff53e81c0cc7d0544bf

main merged, policy_lint.mjs resolved by union. The merge of origin/main (#3305, merge 5e1ffb34) conflicted in one hunk of tools/policy/policy_lint.mjs: this PR inserts `figureBlockProblems` before `checkPrBody`, #3305 widens the `checkPrBody` signature with `required = null`. Resolution: both kept, so the signature carries `required` and `figureBlockProblems` is present and called (`figureBlockProblems(body, { base, head })` in checkPrBody). Resolution delta against origin/main in that file: only the `figureBlockProblems` function and its call and self-test uses (`git diff origin/main fcd03452c -- tools/policy/policy_lint.mjs`). tests/closures.json merged by its driver. Confirmed present after the merge: #3305's `required` option, its `required()` read for silent reds, and its self-test arms (reqGot, unreadSet, owed-reds stub); this PR's `figureBlockProblems` and its self-test arm. `node tools/policy/policy_lint.mjs --self-test` exits 0 (FIXTURE ok); `tools/pr/prepr.sh` at this head exits 0 (mode FULL, closures skipped as unscopable). fcd03452c is the conflict merge a5fd59d19 plus the wip marker merge (identical tree). Null control: `git merge-tree --write-tree origin/main fcd03452c | grep -c CONFLICT` prints 0.

## Mutation proof

`figure_block.py --self-test` mutants: hand-typed value, moved head, unregistered/head-only instrument, unknown name, non-zero exit each fail their check; `body_push.sh --self-test` deletes the `# mut:keep` refresh line and its arm fails; `policy_lint.mjs` registers `figureBlockProblems` as a return-mutant site. Earlier repair: reverting the figure_block.py hunk makes `tests/throwaway_git.py --check` refuse `tools/pr/figure_block.py` and the prepr self-test fail its two raw-git checks. The merge adds no production line of its own.

## Null control

Pin removal on a scratch worktree of 566ff8352 (`git worktree add --detach`), `node tools/policy/field_coverage.mjs`:

- governance.yml pin step deleted alone: `FIELD COVERAGE ok`, rc=0, the entry still listed as `none pinned tools/pr/figure_block.py`, because `codeowners_gap.py` still prints `PINNED tools/pr/figure_block.py` from pr-contract.yml (its output with only that step removed still names it).
- both pins removed (the governance.yml step and the pr-contract.yml step `Every figure block is what its registered instrument renders`, each deleted whole): `DEAD registry: DECLARED \`pinned tools/pr/figure_block.py\` is no longer in the derived set`, `RESULT ... declared_none=37 ... dead=1 refused=0`, `FIELD COVERAGE REFUSED`, rc=1. `codeowners_gap.py`'s `PINNED` set, sorted and diffed against the unperturbed tree, loses exactly `tools/pr/figure_block.py`. (A first attempt renamed pr-contract.yml's `run:` path instead of deleting the step; that also dropped `PINNED tools/pr/preflight.sh` and `tools/pr/prepr.sh` and read dead=3, so it was discarded as a perturbation wider than the claim.)
- restored (`git checkout .github`, `git status --short` empty): `RESULT ... declared_none=38 ... dead=0 refused=0`, `FIELD COVERAGE ok`, rc=0, the entry back as `none`.

## Figures

No block is used in this body: the registry does not exist at the base, so this pull request cannot use its own instrument. Free-form, each run at 566ff8352:

- `node tools/policy/field_coverage.mjs` printed `RESULT read=56 ignored=28 declared_none=38 blind=0 dead=0 refused=0 runs=146` and `FIELD COVERAGE ok`, rc=0; `figure_block.py` listed as `none`, not dead and not pending (no `pending` line printed).
- `node tools/policy/field_coverage.mjs --self-test` printed `FIELD COVERAGE SELF-TEST ok`, rc=0.
- `python3 -I tools/pr/figure_block.py --self-test` printed `figure_block self-test: 11 checks, 0 failed`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2668 ENTITY CHECKS PASSED`, rc=0 (its `FAIL` lines, e.g. `a3:roster`, `a3:orjson`, are planted-input arms inside its checks; the verdict line is the one quoted).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: FULL` (reason: `tests/closure.py changes the gate itself`), so the scripts are left to CI.
- `tools/pr/prepr.sh` with `PREPR_SKIP_CLOSURES=1` at 566ff8352 printed `PRE-PR: 566ff83528c66d3edd20e5ae7cd3cd3038e00745 000000000000000000000000000000000 rc=0` (`ci predict`: no red predicted against 51cd5ec8a42a; `self-test`: 516 passed, 0 failed). origin/main, re-fetched after the run, was still 51cd5ec8a, so no further merge was needed. Null control at main for that skip: the only closures delta against origin/main 51cd5ec8a is the two members named above, the same two the tip added, so the skipped recording step can find nothing the merges introduced; closures-autofix owns it on the pull request.

origin/main measured at 51cd5ec8a (committed 2026-11-08T21:20:13+01:00; fetched 2026-11-08T20:32Z).

## Approval

Policy files touched (policy_lint.mjs, PULL_REQUEST_TEMPLATE.md, pr-contract.yml, field_coverage.mjs): owner approving review needed, or the card-7 mandate under which the orchestrator ruled this build.

## Red checks

`governance / delivery-status` is red at 7c586c7cf (job 128960422153, run 42554818800) and it is main's red, not this diff's: it grades main's delivery rows, and its log reads `DELIVERY STATUS OVERDUE — 0 rowed, 12 pending, 3 overdue (overdue at 12 commits)`, with the overdue rows #3333, #3316 and #3318, record PRs held for the stamp. This diff edits `.github/workflows/governance.yml` (the figure-block self-test step), so the body exemption does not apply and the red is named here. Evidence: the identical line prints on #3360 (job 128988774945) and #3350 (job 128985523599) at 2026-11-09 05:09 and 05:00Z, with the same three overdue rows. #3360's diff touches only its own delivery row, none of this check's inputs. The check's own text says it is not a required context. Cheaper detector: none; `tools/audit/seat/delivery_row.sh` and the check itself already catch it, and the standing cost is the stamp draining the rows, which this PR cannot do. Carry: dismissed: main's overdue rows pending the stamp, not this diff.

none other predicted: the earlier `governance / policy-docs` refusal is answered by the base's pending entry (#3312).

## Forward-carry

none

## Friction

none
