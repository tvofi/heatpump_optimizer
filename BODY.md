HOTFIX brief-lint maxBuffer (proposal `PROPOSAL-brief-lint-treelisting-maxbuffer`, legal mid-round: it prevents a certain main red). `treeListing` in `tools/policy/brief_lint.mjs` ran `git ls-files` / `git ls-tree -r --name-only` through `execFileSync` with Node's default 1 MiB `maxBuffer`. The tracked listing now sits just under that cap on main and over it at the heads of #3822 and #3824, where the linter dies with `spawnSync git ENOBUFS`. Every check that imports or runs the linter goes red with it: policy-docs, env-matrix, wave-script, instrument-self-tests, briefs, graders-head-copy, pr-contract and gate. Main goes red when either PR lands.

The fix gives the cap one owner. `tools/policy/counts.mjs` already read git with a 64 MiB `maxBuffer`. It now exports that helper as `gitRead` with the constant `GIT_MAX_BUFFER`. `treeListing`, `brief_lint.mjs`'s `git` helper and `agreement.mjs`'s `git` helper all route through it. Alternatives that lost:
- Adding `maxBuffer` to `treeListing` alone (the proposal's one line) leaves the same 1 MiB cap in two more helpers that read the full listing. One of them, `refFiles`, reads with `allowFail` and would turn an overflow into a silently empty listing at a cited tag.
- A literal per call site repeats the constant in three files, so the next helper copies whichever one it finds first.

`policy_lint.mjs`'s own helper already carries the 64 MiB cap and is left alone: it is outside this hotfix's reach, and it is not in the class.

The failing test came first: commit `0d40b70c9d` adds `treeListingOverDefaultBuffer` to `assertTreeRev`. It fills a throwaway repo's index by plumbing (`update-index --index-info`, with no files on disk) until the listing is over 1 MiB. Then it requires both forms, rev (`ls-tree`) and checkout (`ls-files`), to return every probe path. It asserts its own precondition: if the probe listing is not over the 1 MiB default, the check refuses as vacuous instead of passing.

## Head

54700c2fe43d1e9ea817a406da280680d5bb4386, two commits on origin/main 6fdc15354f0f6f4613370fdabe4bd82adbadc087, measured 2026-11-21T21:47Z. `git merge-tree --write-tree origin/main HEAD` prints one tree.

The finder's harness (the proposal's symptom) loads `treeListing` from each tree and lists three revs in this repository: `node --input-type=module -e "import('./tools/policy/brief_lint.mjs').then(m => m.treeListing('<rev>', '<repo>'))"`.

| tree | origin/main 6fdc15354f | #3822 head 89ec15b79b | #3824 head 4b0f3eb96a |
|---|---|---|---|
| base 6fdc15354f | ok, 1033283 bytes | `ENOBUFS` | `ENOBUFS` |
| head 54700c2fe4 | ok, 1033283 bytes | ok, 1074652 bytes | ok, 1069422 bytes |

## Mutation proof

The mutant deletes `maxBuffer: GIT_MAX_BUFFER, ` from `gitRead` in `counts.mjs`, which is the one production line the fix rests on. It was applied in a detached worktree at the head. `assertTreeRev`, the TREEREV acceptance that `node tools/policy/brief_lint.mjs` runs on its no-argument path, was driven directly through a scratch export shim, the same function the CLI calls. The result is rc 1:

```
TREEREV VACUOUS:
  the rev listing over the default maxBuffer threw (ENOBUFS)
  the checkout listing over the default maxBuffer threw (ENOBUFS)
```

The test-only commit `0d40b70c9d` (the test before the fix) prints the same two lines, rc 1. The head prints `TREEREV ok`, rc 0. The diff adds no `.py` lines outside `tests/` and `dev/`, so prepr's mutant draw has nothing to sample. The mutated line is a `tools/` site that `mutation-autofix` does not mutate, and the TREEREV acceptance above is its in-tree killing check.

## Null control

- On the unmodified tree, a listing under the cap works: the base row for origin/main in the Head table, 1033283 bytes, lists fine. The defect is the cap, not `ls-tree` itself.
- The probe's own null: at the head, shrinking the probe to 512 KiB (`bytes <= 512 * 1024`) makes the check refuse rather than pass, rc 1: `the rev probe listing is 524454 bytes, not over the 1048576-byte default: vacuous` (and the same for checkout). Without that guard, a probe that shrank under the cap would pin nothing.

## Figures

The scope-line figure block is omitted. The gate's MODE line at the head, from `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`, is `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and the script run is `tests/entities.py`.

- Listing size per rev: `git ls-tree -r --name-only <rev> | wc -c`. origin/main 6fdc15354f gives 1033283; #3822 head 89ec15b79b gives 1074652; #3824 head 4b0f3eb96a gives 1069422. Node's default cap is 1048576.
- The class, enumerated by rule (fixer step 8): `git grep -nE "['\"](ls-files|ls-tree)['\"]" -- 'tools/*.mjs' 'tools/*.js' 'tools/*.cjs' 'tests/*.mjs' 'tests/*.js' 'tests/*.cjs' '.claude/*.mjs' '.claude/*.js'` lists every Node read of a tracked listing. Each line, with its disposition:
  - Closed in this diff, through `gitRead`:
    - `brief_lint.mjs` `treeListing` (ls-tree / ls-files)
    - `refFiles` (ls-tree at a cited tag, `allowFail`)
    - `assertGrepExcludeBounded` (ls-files)
    - `agreement.mjs` `governanceCode` and `mergeSubjectGuard`'s `tools .claude/workflows` listing
  - Already guarded at 64 MiB:
    - `counts.mjs` `lsFiles` and its three `derivations` reads, now `gitRead`
    - `policy_lint.mjs`'s `git` helper: `refFiles`, the tracked-files loop and `_printerSource`
  - Not the tracked listing:
    - `tests/card.mjs`, a stubbed `runGit` that spawns nothing
    - `tests/card_rig.mjs` `threeDotFiles`, untracked files and a diff, through an injected `runGit`
- The same helpers' `git grep -I -l` reads, whose output is bounded by the listing, go through the guarded helpers: `brief_lint.mjs` (`symbolInTree` and `symbolInRefTree`) now, and `policy_lint.mjs` already.
- Python's `subprocess` has no output cap, so the `tools/` and `tests/` Python callers are outside the class.
- Every Node `execFileSync`/`spawnSync`/`execSync` call in `tools/` and `tests/` with no `maxBuffer` in its call text was scanned (a scratch scanner that reads each call to its closing parenthesis). The scan listed no tree-listing read beyond the helpers above. The rest are `gh` calls, single-object `git show`/`rev-parse`/`merge-base` calls, and agreement.mjs fixture strings.
- The TREEREV probe's added cost, `assertTreeRev` timed at the head: 2242 ms under a load average near 44 on this host.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Agreement lane, as CI runs it: `python3 -I tools/policy/agreement_py.py --out $J && node tools/policy/agreement.mjs --py-json $J` prints `AGREEMENT ok`, with `RESULT divergent=0 unregistered=0 dead=0 refused=0`. `node tools/policy/agreement.mjs --self-test`: 233 of 233 probes held.
- `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`: rc 0. It skips brief_lint, policy_lint and the agreement lane, so the three bullets above are run by hand.

## Red checks

The defect turned #3822 and #3824 red on policy-docs, env-matrix, wave-script, instrument-self-tests, briefs, graders-head-copy, pr-contract and gate. None of them is this PR's. The cheaper detector is the TREEREV acceptance added here. It already runs inside `node tools/policy/brief_lint.mjs`, so it adds no new lane, at a measured standing cost of about 2 s per run. It is cheaper than the gate that found the defect because it fails on any tree, before the real listing crosses the cap, instead of on the one PR whose additions push it over. Before this diff nothing measured the buffer, so the failure was invisible until a PR crossed 1 MiB.

## Forward-carry

The remaining process question goes to the root-cause seat the orchestrator runs beside this fix (`defect-root-cause.md`): whether a static refusal of a Node `*Sync` git read without `maxBuffer` outside `gitRead` pays its cost test. Carry: dismissed: owned by the orchestrator's parallel root-cause seat for this hotfix, not this fix's seam.

## Friction

none
