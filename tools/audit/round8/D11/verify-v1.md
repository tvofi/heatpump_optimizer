# D11 round 8: verifier v1's report

- Seat: D11-v1. This round has one verifier (the owner's call), so this report covers both halves of `verifier.md`.
- Tree: `/home/claude/audit-r8/seats/D11-v1`, a git worktree at `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Earlier rounds are stripped, as in BASELINE.md.
- Finder evidence: copied in with `cp -rn` from D11-s1 and D11-s2. No finder harness hard-codes its seat path, so every one ran unchanged from this tree.
- Environment: `PYTHONPATH=tests/hastub`, all five BLAS thread variables set to 1, and `TMPDIR`/`HPO_PLANDATA` under `/home/claude/audit-r8/tmp/D11-v1`.
- Box load: load1 was 22 to 25 throughout, and `thread_factor` was 1.000 to 1.001 on every run.
- Timing: no finding here rests on a timing number. Every value below is a count or an exit code, so none of them is provisional for load. The live GitHub data can still grow.
- Tree state at exit: production files are byte-identical to the baseline. `git status` shows only `?? tools/audit/round8/` beyond the stripping deletions, and `v1_owner_flip.py` asserts `tree_dirty_after=0`.
- GitHub reads: unauthenticated `curl` GETs to api.github.com (public repo), read-only. The `/rate_limit` path is blocked in agent sessions. Nothing was posted.

## Summary

| id | finder value | re-run of the finder's harness | my harness, my value | vote |
|---|---|---|---|---|
| D11-s1-01 | 3 | 3; perturbed 0; null 0; history 3 merged of 15, 6 of 18 | `v1_latest_order.py`: 21 pairs. By id 16 are latest-skipped, by started_at 5, by completed_at 3; 18 of 21 are races | weaken (high) |
| D11-s1-02 | 14 | 14; perturbed 13; null 37/0 | `v1_owner_flip.py`: 18 candidates unowned, 5 flip a red required command to rc=0 | weaken (medium); same mechanism as s2-01 |
| D11-s1-03 | 2 of 4 | 2 of 4; perturbed 0; null 0 | `v1_stop_index.py`: 3 of 6 blind (2 of the finder's 4); perturbed 1 of 6 (0 of 4) | verify (low) |
| D11-s2-01 | 8 | 8; flips 3 of 3; null rc=1; all 8 owned gives 0; 5 owned gives 3 | `v1_owner_flip.py`: counts/render_md/markdown-it each flip 1 to 0; unloaded null rc=1 | verify (high); same mechanism as s1-02 |
| D11-s2-02 | 2 of 2 | off_main 2 of 2, on_main 2 of 2; perturbed 0 of 2 and 2 of 2 | `v1_release_controls.py`: 0 controls (workflow 0, active tag rulesets 0); perturbed 1; null name_refusals=1 | verify (high) |
| D11-s2-03 | 12 | 12; perturbed 11 | `v1_pins.py` over all workflows: 12 unhashed, 1 not even version-pinned, `uses` unpinned 0; perturbed 11 | verify (low) |

---

## D11-s1-01: a body edit re-reports three required contexts as `skipped`

**My metric:** over the merged PRs after 51b0742 plus the open PRs, count the (head, required-context) pairs where a `skipped` run and a non-skipped run of the same name coexist at one head. Split them by which run is the latest under three orderings: check-run id, started_at and completed_at.

**Re-run of `s1_skip_supersede.py`:**
- Tree arm: `required_skippable_edited=3` (env-matrix, policy-docs, wave-script). `--perturb` gives 0. The synchronize null gives 0. The dispatch arm gives recheck=true 1 (closure-scope) and recheck=false 5.
- History arm, with `--clone /home/claude/heatpump_optimizer`, a shallow clone that still contains 51b07423: 15 merged plus 3 open PRs. `superseded_heads=6`, `superseded_merged_heads=3` (#1484, #1485, #1488), `masked_red_heads=0`. This reproduces the finder's numbers exactly.

**My harness, `v1_latest_order.py`:**
- `pairs=21` across 7 heads. The finder's 6 heads plus #1489, where a later real run follows the skip.
- `other_suite=21`: every skip comes from a second check suite, meaning a second event.
- `latest_by_id=16`, `latest_by_started=5`, `latest_by_completed=3`.
- `race_pairs=18`: in 18 of the 21 pairs, the skipped run completed before the real verdict did.
- Null control: 0 pairs on the 13 non-governance required contexts.
- Perturbation (drop the check suites the edit produced): 0.

**Attacks, in `verifier.md`'s order:**
1. **Contention:** not applicable. Every value is a count.
2. **Gate mode:** not applicable.
3. **Grid artefact, and the "latest" ordering.** The finder orders runs by id, and the 3-of-15 merged figure depends on that choice. Most pairs are a race: the `edited` event fires within seconds of `opened` (#1488: skip at 15:50:31, real policy-docs completed at 15:51:12), so the skip is created later but completes earlier.
   - Ordered by completed_at, only #1484 (3 pairs) is superseded. That is 1 merged head, not 3.
   - The repository's own record says "required checks are evaluated on the latest run per name" (`docs/plan-2026-09-open-issues.md:1556`, observed on #656). That observation was a later-created, later-completed success, so it does not separate the two orderings.
   - The check-runs API does not settle it either: `filter=latest` and `filter=all` both return both policy-docs runs at 09d62a1c.
   - The hop remains unprobed, as the finder says.
4. **Null control:** present and passing, in both harnesses.
5. **Reachability.** The mechanism is real and routine: 7 of 18 heads carry it. But the consequence splits by ordering:
   - **If completion order decides:** only an edit made after the red has completed supersedes it. In that case `pr-contract`, which re-runs on `edited`, lists every `failure` at the head, earlier runs included (governance.yml, "List the red checks at this head"). The body must then answer policy-docs under `## Red checks`, so the red is surfaced and not silently masked.
   - **If creation order decides:** the routine race masks silently. The edited run's `pr-contract` takes its red list before the real verdict exists. Its own success (created later) would also supersede the `opened` run's pr-contract result.
6. **Severity.** Critical is not earned on what was measured:
   - No red has been masked (`masked_red_heads=0`).
   - The load-bearing hop is unprobed.
   - Under one of the two plausible orderings, the red is forced into the body.
   - The approver path (`app_approve.sh`) also requires a fix-review `merge` verdict.
   - I would give it **high**: a required refusal can be made advisory, or silent under creation order, by a routine event.

**Vote: weaken (high).**

---

## D11-s1-02 and D11-s2-01: one mechanism, the CODEOWNERS enforcement surface

Both findings come from the same root: R6's `codeowners_gap.py` rule sees only `<interpreter> <path>`. It does not follow `./path` executions, imports or data reads.

The two finders' sets overlap on 4 files (`tests/run.sh`, `tests/derive_closures.sh`, `counts.mjs`, `render_md.mjs`). The union is 18 files.

**My metric:** of the 18-file union, count the files that (1) no owner-bearing CODEOWNERS pattern matches, using my own last-match resolver, and (2) where a one-line edit to that file alone turns a red run of a required context's own command into rc=0, in the PR checkout (not restored from base).

**My harness, `v1_owner_flip.py`:**
- `unowned_candidates=18`.
- `unowned_flipping=5`, each driven as a process:
  - `counts.mjs`, `render_md.mjs` and `vendor/markdown-it.min.js`: pr-contract's `policy_lint.mjs --pr-body <empty>` goes from rc 1 to 0 when one `process.on('exit')` line is appended to any one of them.
  - `policy_known_bad.json`: `node policy_lint.mjs` is red at this stripped, shallow baseline (7 citation errors). It goes from 1 to 0 once the ledger is grown with `--record-known-bad`. That command wrote only that file (checked with `git status`). governance.yml's restore step deliberately does not restore this ledger, so in CI the PR's own copy grades the PR.
  - `tests/run.sh`: with `PYTHON=/bin/false` it is red (rc 1). It goes from 1 to 0 with `exit 0` inserted as line 2.
- Null control 1: the same append to `tests/card_rig.mjs`, which is not loaded, gives rc=1.
- Null control 2: the same append to the owned entry file `policy_lint.mjs` also gives rc=1, because the entry exits synchronously first. So the flip is a property of import order, not of "any append".
- Perturbation (own every candidate): 0.

**Re-run of `s1_owner_surface.py`:** 14 (3 exec, 2 import, 9 data); `--perturb` gives 13; the null control gives surface 37, uncovered 0. This reproduces the finder exactly.

**Re-run of `s2_owner_closure.py`:**
- `unowned_required_closure=8`, `pr_contract_flips=3 of 3`, `null_control_unloaded_file_rc=1`.
- With all 8 owned (`--extra-owner` x8): 0. With only the 5 governance files owned: 3. This reproduces the finder exactly.
- The claim that pr-contract and briefs do not restore their check source from base checks out: governance.yml's restore step exists only in `policy-docs`.

**Attacks:**
1. **Definition artefact in s2-01's count of 8.** It includes 3 test modules (golden, harness, profiles) because they are imported, but it stops at `run.sh`. Expanded through `run.sh`, which `fast` executes, 33 of 43 top-level `tests/*.py`/`*.mjs` are unowned. That is by design: code PRs go to the App reviewer (CLAUDE.md, decision 0011). The defensible core of the defect is the governance loaders, plus `run.sh`, which the CODEOWNERS header's own rule ("the scripts their non-comment lines execute") covers via `./tests/run.sh` (tests.yml:312, 749).
2. **Padding in s1-02's count of 14.**
   - `tools/audit/w5-partition/coverage_tree.sh` runs only in `coverage`, which is not a required context, and runs under `|| true`. It carries no verdict.
   - `tests/closures.json` and both claim files are written routinely by the `closures-autofix`/`claims-autofix` bots and by fixers (`ci-autofix.md`). Owning them would put an owner review on the documented bot path, so they are not an omission of the same kind.
   - `requirements-ci.txt` is arguable.
   - The defensible core is about 10, of which 5 flip dynamically (above).
   - The budget-file arm (`structure_budgets.json`, `policy_budgets.json`) is real: CLAUDE.md rule 2 wants the owner's confirmation for a raise, and nothing mechanical enforces it. But a raise passing the ratchet is the file's intended semantics, not a check being neutered.
3. **Null controls:** present and passing in all three harnesses.
4. **Reachability:** real. The PR author is the `hpo-author` App, and a non-code-owned PR merges on `hpo-approver` after a fix-review `merge` verdict (`app_approve.sh`). No owner review is ever requested for these paths. This is the gap R6-D11-01/#1402 was meant to close.
5. **Severity:**
   - s2-01 keeps **high**: its dynamic flip on pr-contract is the sharpest demonstration, and it names the missing restore-from-base on pr-contract and briefs.
   - s1-02 is the same mechanism with a padded count. I would give it **medium** as a separate row. The judge should merge the two findings.

**Votes:** s1-02 weaken (medium); s2-01 verify (high). They share one mechanism.

---

## D11-s1-03: `stop-selfcheck.sh` does not read the index

**My metric:** of six end-of-turn policy-touching states, count those where the real hook exits 0 while a stub linter exits 1. The states are committed, unstaged, staged, staged_new, untracked_new and staged_then_reverted_worktree.

**Re-run of `s1_stop_hook_states.py`:** 2 of 4 blind (staged, staged_new); `--perturb` gives 0; the null gives 0.

**My harness, `v1_stop_index.py`:** it builds its own scratch repository and origin, and runs the real hook with `CLAUDE_PROJECT_DIR`.
- `blind_states=3` of 6: staged, staged_new and untracked_new. `blind_finder_four=2`.
- staged_then_reverted is caught, because the unstaged diff sees the index/worktree difference.
- Null control: `null_red_blocks=0`.
- A production-only change exits 0, as designed.
- `--perturb` (append `git diff --cached`): 1 of 6, 0 of the finder's 4. The remaining untracked_new is moot, because `policy_lint` reads its corpus through `git ls-files` and would not lint an untracked file either.

**Attacks:**
- No contention or gate-mode issue.
- Reachability: a turn that ends with staged but uncommitted policy edits is a normal state.
- Consequence: small. `policy-docs` and `pr-contract` refuse the red in CI, and the hook is a one-shot prompt by its own design ("a prompt to look, not a cage").

**Vote: verify (low).**

---

## D11-s2-02: release.yml publishes and attests any `v*` tag without checking it is on main

**My metric:** count the controls between a write-capable push of a `vN.N.N` tag (or a dispatch) at a commit not on main and `gh release create` plus the attestation. Four kinds count:
- (a) an ancestry test in a step before `gh release create`;
- (b) a main-ref `if:`;
- (c) a job `environment:`;
- (d) an **active tag-target repository ruleset**, read live.

**Re-run of `s2_release_gate.py`:** off_main 2 of 2 published and digested; on_main 2 of 2. With `--perturb`, off_main is 0 of 2 and on_main 2 of 2. This reproduces the finder exactly.

**My harness, `v1_release_controls.py`:**
- `controls=0`: workflow 0, tag rulesets 0.
- The live `GET /repos/tvofi/heatpump_optimizer/rulesets?includes_parents=true` lists only `main-protect` and `main-protect-checks`, and both are `target: branch`, `~DEFAULT_BRANCH`.
- Null control: `name_refusals=1`, the vN.N.N regex, so the parser does see refusals.
- `--perturb`: `controls=1`.

**Attacks:**
- **Reachability.** This closes the finder's provisional hop: no tag ruleset exists, so a tag push by any `contents: write` identity reaches the job.
  - Caveat: the ruleset list was read unauthenticated. A ruleset hidden from anonymous readers cannot be excluded, but ruleset listings of a public repository are normally visible.
  - The dispatch path also needs `actions: write`, which I did not measure; the tag path suffices.
- **Consequence.** A published GitHub release is what HACS installs, and the provenance attestation names release.yml as signer. An unreviewed commit could therefore ship to users under a valid-looking attestation.
- **Severity:** high is earned.

**Vote: verify (high).**

---

## D11-s2-03: 12 CI install commands are not hash-pinned

**My metric:** install commands in every workflow's `run:`, tokenised with shlex, that are not hash-pinned in Scorecard's sense. The typing requirements are resolved by running `tests/typing_ruler.py --print-requirements`.

**Re-run of `s2_scorecard.py`:** 12; `--perturb` gives 11.

**My harness, `v1_pins.py`:**
- `unhashed_installs=12`. All 12 are in tests.yml; the other workflows contribute 0.
- `version_unpinned=1`: the typing venv, whose requirements are `aiohttp numpy scipy-stubs threadpoolctl voluptuous` with no version.
- `uses_unpinned=0`: the null control holds.
- `--perturb`: 11.

**Attacks:**
- No contention.
- My first pass missed the `npx` that follows a `VAR=value` prefix. Fixed, and the count agrees with the finder.
- Consequence: a Scorecard score and a supply-chain hardening gap, not a broken check. The typing one is the most consequential, because unversioned names can move the typing ruler's numbers.
- Severity: low is right.

**Vote: verify (low).**
