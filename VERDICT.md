Fix review: merge d760cbe35ec9114d58ae4d2e329512b270e95428
bus-nonce: 13598ff1fb74a140fe0311a3780b1453

Reviewer seat review-2027-r2, **round 2** of PR #2027 (R9-RO-10). I measured head d760cbe35ec9 from a detached worktree. The head's tree is identical to the code head f4d102a0, and its merge base is 09ba95d0. Main is now c327da7f (#2002); merge-tree against it exits 0. The head was unchanged when I posted. Evidence is in /Users/timmalmstrom/hpo-seats/review-2027-r2/ev.

## Round-1 blocks: each one re-checked

**1. Dead `inert_reads` (closure.py check and prune): resolved.**
- `check()`'s PHANTOM sweep and `prune()` now iterate over `closures` and `inert_reads`.
- `prune` drops an `inert_reads` key that is left empty. That matches `_fold_inert_reads`, which writes no key for a script that read nothing.
- My mutants on `tests/closure.py selftest` (`closure-mutants.txt`):
  - check reads `closures` only: 1 red.
  - prune reads `closures` only: 1 red.
  - prune keeps the empty key: 1 red.
- I planted a dead `inert_reads` path in the real `tests/closures.json` (`tests/doc_claims.py` -> `tools/audit/eg_b7_seam_hubs.py`). `closure.py check` printed `PHANTOM ... tests/doc_claims.py (inert_reads): ...` with rc=1, and `prune` removed exactly that entry. With the plant restored away, check got past the phantom stage.
- Dead `inert_reads` entries number 0 at the head and 0 on main c327.
- All three parts of the roster carry are delivered.

**2. The guard's exemptions are keyed per path: resolved.**
- I called `stale_lines` directly against the real retired entries (`sneak-cases.txt`). Each of these is refused:
  - a bare `# layout:old`;
  - a marker naming another path;
  - a marker naming a prefix of the path, or a longer path;
  - `layout:old= <path>` with a space;
  - `locate()` of another path;
  - `relocate(<same path>)`;
  - an unquoted `locate(path)`;
  - prose that names the marker word;
  - a two-path line whose marker covers only one path (the other path is refused).
- The keyed marker and `canon("<path>")` pass, as intended.
- No retired entry's new path is a substring of its old path (0 of 158).
- Layout mutants against `--self-test` (`layout-mutants.txt`):
  - M6, the unkeyed marker: 3 cases red.
  - M7, the unkeyed `locate`: 1 red.
  - Dropping the new-path arm: 1 red.

**3. The finder wall in `prepare_baseline.sh --strip`: resolved.**
- `--strip` now calls `finder_wall`, and the wall covers `dev/programme/register/audit-*.md`.
- Both `audit-find.js` prompts call the script instead of a hand-written list.
- No other live wave script lists the wall's globs. I grepped `.claude`, `tools`, `dev/governance`, `docs`, `CLAUDE.md` and `AGENTS.md`.
- Mutant, `finder_wall` removed from `--strip`: `--wall-self-test` prints `FAIL --strip kept the programme register`, rc=1.
- Simulated export of `git archive origin/main` (c327) put through the head's `--strip`: `register_survives=no`, `setup_kept=yes`.

**4. The five re-pointed lines and the `rotation.json` handling: resolved.**
- `dev/audit/config/{bugclasses,finding.schema,rotation,scopes}.json` all exist.
- The head's `check-wave-script.mjs` prints 170 passed, and main's (c327) copy on the head tree also prints 170 passed.
- I tested the writer-prompt parenthetical both ways (`cws-mutants.txt`):
  - with the parenthetical dropped, main's checker fails 2;
  - with only the old path, the head's checker fails 2.

  So the dual spelling is required while policy-docs grades with the base checker.
- Guard simulation of this PR merged onto main c327: 0 refusals.

**5 and 6. Rule globs, including the kept `tools/audit/briefs/**`: resolved.**
- `dev/governance/**` covers the 15 dimension and 8 role files.
- I dropped the canon `tools/audit/briefs/**` glob from `defect-root-cause.md` and regenerated the copies with `rules_sync`. `policy_lint` then printed `TOTAL: 23 error(s)`, all of them rule-binding. That is the body's figure, re-derived.
- At the head:
  - `policy_lint` prints TOTAL 0 and FIXTURE ok;
  - `rules_sync --check` prints ok;
  - the dead-glob loop prints exactly the 2 kept canon globs.

  Their retirement is carried in `carry-1922.json` (`brief_lint` 0).

**Merge-order note with #2014: confirmed**, against #2014's current head 1d494f01 (`merge-order-sim.txt`):

| order | guard refusals |
|---|---|
| this PR onto main | 0 |
| #2014 after this PR | 2 new-reference, exactly the body's `tests/entities.py` and `tools/pr/preflight.sh` lines |
| this PR after #2014 | 0 |

## Other checks

- VERSION, the manifest, the RELEASE_NOTES heading and both claim files are untouched (three-dot diff).
- The `custom_components` edits are comment and docstring path re-points only.
- `structure.py` prints PASSED.
- The layout self-test is ok. `--guard` against 09ba95d0 gives 0 refusals.

## Non-blocking, for the fixer's discretion

- **Surviving mutants, all in self-tests.**
  - M8: dropping the marker's `(?![\w./-])` boundary survives `--self-test`. The code is correct (my sneak case refuses a longer-path marker), but nothing pins it.
  - M10: dropping `.claude/rules/` and `.cursor/rules/` from GUARD_EXEMPT survives the self-test. The real diff does catch it: 1 refusal on the `.cursor` `globs:` line.
  - Mc4: `prune` also deleting an empty `closures` key survives `selftest`.
- **Exemptions the body accepts by design**, keyed to the same path:
  - a line that also carries `locate('<old>')` passes an executed citation of that same old path;
  - a stale command with the new path in a trailing comment passes.
- **Two body inaccuracies, neither of which moves a figure.**
  - The body says R9-RO-9 drops the `audit-verify.js` "(tools/audit/rotation.json before R9-RO-8)" parenthetical. Neither `carry-1922.json` nor the roster carries that. It is harmless cleanup, droppable by anyone once this PR's checker is main's, so it is not a carry-missing.
  - The Head section says d760 merges origin/main. Its parents are actually 43883893 and f4d102a0, and the two trees are identical.

## CI at the head (check-runs API, final)

- 24 success, 12 skipped, 2 failure.
- Success includes:
  - fast (3.14), closures, coverage, coverage-ratchet and mutation;
  - CodeQL, including Analyze (python);
  - Validate, Hassfest and PR contract;
  - budget-raise-gate ×2.
- budget-raise-gate: the cancelled twin (run 37661198391) was rerun by me with `gh run rerun` and is now success.
- delivery-status: red on main's unread rows (#1989, #1991, #1992, #1998 and others), not this PR's.
- nightly-status: inherited.

  The body answers both reds.
- mutation: the production diff is comments only, so no production mutants were drawn.

## RESULT

```
RESULT closure_mutants killed=3 survived=1 (Mc4 pre-existing closures arm, untested)
RESULT closure_real_plant phantom_inert_reads rc=1 pruned=1; dead_inert_reads head=0 main_c327=0
RESULT guard_sneaks refused=all unkeyed/other-path/prefix/extended/space/relocate/unquoted/prose; keyed=0
RESULT layout_mutants killed=3 (M6,M7,new-path) survived=2 (M8 boundary, M10 copies-exempt: real diff catches)
RESULT wall_mutant no_wall_in_strip=FAIL rc=1; sim_export_main_c327 register_survives=no
RESULT check_wave_script head=170/0 main_checker_on_head=170/0; parenthetical_needed=both arms 2 failed
RESULT policy_lint head=0 drop_canon_briefs_glob=23 rule-binding
RESULT dead_globs head=2 (kept canon, carried)
RESULT merge_order 2027_onto_main=0 2014_after_2027=2 2027_after_2014=0
RESULT ci_head success=24 skipped=12 failure=2 (delivery-status, nightly-status: inherited)
```

My verdict covers correctness only. This PR edits policy and code-owned `tests/closure.py`, so it still needs tvofi's approving review at the head.
