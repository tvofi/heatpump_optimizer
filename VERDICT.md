Fix review: blocked a3734e793d451cf6af658dcf9d5500fd093f403a harness: class-open a head .gitattributes export-ignore hides code from the base-run gate's git archive

bus-nonce: 6917a92a1e483105e9d57f3d3db0e94c

Round 2 (the round-1 record is VERDICT.md on review/2068 at af9929a4, which was not posted). Reviewer: review-2068 (opus).

Head measured: a3734e793d451cf6af658dcf9d5500fd093f403a. It is f14e77c9 plus one closures-autofix bot commit ("ci: re-record closures", github-actions[bot]). That commit touches only tests/closures.json (+42/-41): timing values, plus reordered harness entries and an added `.github/workflows/arch-score.yml` entry. It is a normal ci-autofix re-record that touches no code, so every plant below, taken against f14e77c9, applies unchanged.

Checks were settled before posting: 0 pending at 00:47Z, polled every 5 minutes (settle.log).

## Round-1 finding: closed
- arch-score.yml now runs gate.py from `git worktree add --detach "$RUNNER_TEMP/base" "$PR_BASE"`, with `cd` into it and `python3 -I`.
- Emulated locally from a worktree at base f14e77c9:
  - P0, the control (an import cycle, nothing else changed): `FAIL dS -2.7550` (dead_members, import_cycle_modules and public_unused all rise), rc=1.
  - P1, the round-1 plant (P0 plus a tests/structure.py that rewrites `__main__.decide`): now also `FAIL`, rc=1, because the base's structure.py runs.
- Checked against the head, the gate holds on these points:
  - `-I` ignores PYTHON* env and cwd on sys.path.
  - `HERE`, `REPO` and the structure load all resolve inside the base worktree.
  - ARCHSCORE_ABLATE is set only by the workflow, which is owned.
  - The measured tree is parsed, never imported.
  - The self-test also runs from the base.
- The base worktree is the PR's base: PR_BASE is `pull_request.base.sha` (or `merge_group.base_sha`). That is the base branch's tip in the event payload, so the PR cannot set it.
- The no-gate.py fallback: once main holds gate.py, every PR into main takes the base path. A PR opened against another branch that lacks gate.py takes the head path, but retargeting it to main fires `edited`, which re-runs the check on main's base. I found no route back to the head copy into main.
- The workflow file itself is the head's, but `.github/workflows/` is code-owned.
- CODEOWNERS revert: consistent with #201 comment 6070657723 and the base-run design. Not blocking.

## Blocking 1: the head decides what the base-run gate measures, through .gitattributes
`score.tree_of` runs `git archive <ref> custom_components`. `git archive` honours the `export-ignore` and `export-subst` attributes in the tree it archives, so the head's own `.gitattributes` decides which head files the scorer sees.
- **P2:** P0 plus `custom_components/heatpump_optimizer/.gitattributes` marking the two planted modules `export-ignore`. Result: `PASS: dS +0.0000 NULL, no gate metric rose`, rc=0, with the gate run from the base. The cycle ships, because coordinator.py imports it.
- **P3:** the same exclusion through one line in the root `.gitattributes`. `git archive` then holds 0 of the 2 planted modules, against 2 for P0.

Neither `.gitattributes` file is owned. Patches and logs are under evidence/.

Fix: extract the head without attributes, for example with `git ls-tree -r -z` plus `git cat-file blob`, or with a `git --work-tree=<tmp> checkout <ref> -- custom_components`. Alternatively refuse when the head's tree carries export-* attributes reaching custom_components. Add P2 as a planted case in the throwaway-repo drive.

Out of scope: a symlink in the head tree pointing at the base worktree's copy is extracted by tar. That only fools the scorer by shipping a broken module, so I did not plant it.

## Blocking 2: root-cause-unanswered, two reds this diff caused and `## Red checks` does not name
- **`instrument-self-tests`** (job 113598824044; also red at f14e77c9, job 113589829114):
  - `REFUSE tests/arch_score.py:78: subprocess.run([*g, "init", "-q"], check=True)`
  - `throwaway_git: 1 raw git init or clone site(s) refused`
  - This is the new workflow-step drive. It must use the throwaway_git helper. pr-contract at f14e77c9 (113590617450) also refused the unanswered red.
- **`fast (3.14)`**, both runs (113598820837, 113598830001): `FAILED python3 tests/layout.py`, `layout: GUARD: 4 refusal(s) against bd59a4af1b26`. The four are placement refusals for files this diff adds, which sit in no category of tests/layout.json:
  - tools/audit/archscore/gate.py
  - planted/perturb/N5_annotated_return.py
  - planted/redteam/14_hub_write_presolve.py
  - planted/redteam/15_payload_cast.py

  Main's own `fast (3.14)` is green.

The same `fast` runs printed `ALL 171 ARCHITECTURE SCORE CHECKS PASSED` and `ALL 15 ARCHITECTURE SCORE HEAD CHECKS PASSED`. So the planted and red-team verdicts, including rt_14 and rt_15, are as expected.json records. That answers round 1's open point on the red-team plants.

Other reds: `nightly-status` is not this PR's (the body says so).

## Not verified
- C12/C13 mutation proofs: heavy, CI's.
- The red-team sweep's count of 11: not re-derived.
- Step 15 (architecture-sound, fixer.md step 17): the added production lines are workflow and instrument code. No custom_components line is added, and I found no breach.
