R10-996-RUNNER-CLAIMS, second PR (the first, #2843, landed the shape-claim grammar): carries 1 (P196/V116) and 2 (P209/V129). The `claimnotes` driver in `tests/env_drift.py` refused every merge where both sides changed the bare claim list. It now merges that list three-way per scenario (`merge_claim_decision`). A scenario one side changed takes that side's lines. One neither side changed keeps its lines. One a side deleted while the other left it alone stays deleted. It refuses, naming the scenarios, when both sides changed one scenario's lines, or changed claims under `claims-for:` stamps that differ between the two sides.

The stamp and each `may-drift` line merge by the same rule, one key per stamp and per fixture (`merge_marker_decision` over the shared `_decide_per_key`), and the union's copy of those lines is cut to that decision. `merge_claim_defect` compares the result's stamp and `may-drift` lines with the decision exactly, in both directions. A key both sides changed differently is refused and named.

**Round 3 (this push) answers the round-2 review (`verdict/3066` at `5a08ec2e9`).** It adds two commits on that head:
- `a6c237fc2`: both new harnesses find the repository root with the canonical `repo_root` walk-up, not `parents[3]`.
- `76cd77cb0`: the `claims-for:` guard compares this branch's stamp with main's, not all three, which closes the review's S1 finding.

**One rule beyond the carry's text, and why.** On the brief's seven recorded refusals, the per-scenario claim rule alone resolves 2 of the 5 disjoint ones. The other three (#2745 twice, e438816e3) each had one side delete a `may-drift` line, the R8-P3 suspension that claims the fixture for the release, while main left that line alone. Under the per-fixture rule that deletion stands. The alternatives lost: (a) a two-way survival check resolves 2 of 5, which misses the carry's own count; (b) reinstating the suspended line re-exempts a fixture the branch deliberately claimed, and `may_drift_error` then refuses it as `CLAIMED AND MAY-DRIFT` (round 1's D2c).

**Carries 1 and 2 disagree on one case, and carry 1 decides it.** Carry 2 (P209) says "the deletion shape keeps refusing", because "a union would reinstate a claim a side deleted". Carry 1 (P196) rules that a scenario one side deleted and the other left alone stays deleted. A three-way merge reinstates nothing, so P209's stated reason does not hold for that case. Its pinned control is kept as the refusing shape only where a deletion meets a rewrite. `_CM_UNION_IS_SILENT` still pins why a two-way union stays forbidden.

**Carry 3 (P214, the bot's refusal message) is not in this PR.** Its own text says an `edit-brief` taking `tools/pr/merge_main_bot.py` into this group's `files` lands first, and "no fix touches the bot before it lands".

## Approval

Pending. This diff changes `dev/governance/rules/claim-files.md` and its generated copies (`.claude/rules/claim-files.md`, `.cursor/rules/claim-files.mdc`, from `node tools/policy/rules_sync.mjs`), which is policy. It is drafted under mandate 6329234399, as carries 1 and 2 direct. It merges on the orchestrator's approval under that mandate, or on `tvofi`'s approving review at its head. I do not claim either.

The rule as it now reads: the driver "unions the notes and merges three-way claims per scenario and `may-drift` lines per fixture: a side's change or deletion wins over the other's silence". It **refuses** "where both sides rewrote one scenario's claims, one fixture's `may-drift` line or the `claims-for:` stamp, or both changed claims under stamps that differ". Round 2's text said "or stamped differing `claims-for:`". That read as if any stamp difference refuses, but a bump on one side beside the other side's claim change alone resolves (stamp-probe rows S2 and S3, both ends).

## Round-2 findings, all answered

1. **Block 1, `tests / fast (3.14)`.**
   - Cause: `dev/audit/harnesses/claim_merge_mutants.py:28` was `ROOT = Path(__file__).resolve().parents[3]`.
   - Fix: it now inlines `tools/audit/repo_root.py`'s `def repo_root(start)` verbatim, then `ROOT = repo_root(__file__)`. `tests/harness_headers.py` is untouched.
   - The other new harness, `claim_merge_census.py`, had no depth root. It used the caller's working directory for `git` and for `tests/env_drift.py`, so run from elsewhere it measured another tree or crashed. It now inlines the same helper and runs both from `ROOT`.
   - Before (`5a08ec2e9`): `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` gave `1 of 112 HARNESS HEADER CHECKS FAILED`, rc=1, naming `claim_merge_mutants.py:28`. After (`a6c237fc2` and the head): `ALL 112 HARNESS HEADER CHECKS PASSED`.
2. **Block 2, `governance / instrument-self-tests`.** This is main's red, not this diff's. `tools/audit/seat/pr_args.sh` is untouched.
   - Main's own push run 41294924835 (job 124813746788, at `6421fe135`) is red the same way: `pr_args self-test: 158 checks, 2 failed`, `FAIL open_pr: the null control -- an unrelated sleeper survives` and `FAIL null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start`, after ``Security violation: Requested utility `unrelated-sleep` does not match executable name``.
   - The null control is main's preceding push run 41284741462 (`92588d581`), which concluded `success`.
   - The separate R10-HOTFIX-UUTILS-SLEEP PR fixes it.
3. **Block 3, the stale `## Red checks` and the `pr-contract` refusal (`PR-BODY: 2 error(s)`).** `## Red checks` below names every red at `5a08ec2e9` with its cause and cheaper detector.
4. **Finding (a), S1.** Changed, not recorded as a refusal.
   - The S1 shape: both sides bump `claims-for:` to the same release and change disjoint claims. The guard required `base == ours == theirs` and refused it, under a message saying the claims sit under "different" stamps although the two sides' stamps are identical. The same bump with only one side's claim change (S5) resolved.
   - Reason: claims are only incomparable across releases. Two sides that reached one stamp describe one release's diff, the case the stamp's own per-key rule (`mine == main`) already accepts.
   - The guard is now `if both_changed and _parse_claims(ours)[0] != _parse_claims(theirs)[0]`. Claims changed under one side's bump alone still refuse (S4, S10, and the committed null `claims both sides changed under different claims-for stamps are refused`).
   - `claim-files.md` states the rule exactly (see Approval).
   - Failing test first and mutation proof are under `## Mutation proof`.
5. **Finding (b), no `prepr.sh` result line.** `tools/pr/prepr.sh` was run with no closures skip. Its result line is under `## Figures`.
6. **The verdict's two figures it did not re-derive.** Both are re-derived, under `## Figures`:
   - the census per-row counts
   - "8 of 30 failed with `b1a0be47d`'s `env_drift.py`"

## Head

`76cd77cb007ddbd0351d3a27596cadfbdef02439`, measured against merge base `f4a5082a666fcffc4968ed6bc540a6ab3e267c63`. It is the round-2 head `5a08ec2e9` plus `a6c237fc2` and `76cd77cb0`. `origin/main` was `6421fe135` (fetched 2026-11-01). `git merge-tree --write-tree origin/main 5a08ec2e9` exited 0, so the branch was not merged forward. Every figure below was taken at this head unless it names another.

## Mutation proof

**S1, failing first.** The check `claims both sides changed under one stamp both bumped resolve per scenario` was added before the guard changed. The CM section of `tests/entities.py` gave `1 of 31 CM FAILED` (`merged=None`) with the unchanged driver, and `ALL 31 CM PASSED` after. Both runs used the section runner of `claim_merge_mutants.py` on a copy of `tests/`.

**`python3 dev/audit/harnesses/claim_merge_mutants.py`** runs one mutant per rule against the merge-driver section of `tests/entities.py`, now 31 checks. The unmutated copy, run first, is the null control: `RESULT baseline_pass=1`. The result is `RESULT killed=16`, `RESULT survived=0`, `RESULT stale=0`. Two rows are new or re-anchored:
- **N10-stamp-guard-three-way** restores round 2's three-way guard. It is killed, 1 red: `claims both sides changed under one stamp both bumped resolve per scenario`.
- **M4-no-stamp-guard** is re-anchored on the new guard line. Its old text no longer occurs, so it would have printed `stale`. It is killed, 1 red: `claims both sides changed under different claims-for stamps are refused`.

The same harness at `a6c237fc2` (the root fix alone) gave `killed=15`, `survived=0`, `stale=0`, which equals round 2's figure.

**Round 1's `mut.py` over a copy of this head's `tests/`, run by its `cmrun.py`:**
- M1: `11 of 31 CM FAILED`
- M2: 6
- M3: 4
- M6: 1
- R-mine-eq-main-only: 2
- M4: its anchor text (`if both_changed and not (`) no longer occurs, so `mut.py`'s assert stops it. The harness's re-anchored M4 above covers it.

## Null control

- **Stamp probe.** The reviewer's `stamp_probe.py` at `5a08ec2e9` and at this head: only row S1 changes, `refused` to `resolved stamps=['# claims-for: 7.0.5'] claims=['alpha', 'beta', 'delta', 'gamma']`. Rows S2 to S10 print identically at both ends: `diff` of the two outputs, S1 removed, exits 0 (`&& echo` printed `S2-S10 IDENTICAL head vs worktree`). S4 and S10 (claims changed under differing stamps) still refuse.
- **Replay.** Round 1's `replay.sh` runs the driver CLI as git invokes it over P196's seven merges.
  - At the merge base `f4a5082a6`: all 7 `MERGE-CLAIM: refused`.
  - At `5a08ec2e9` and at this head: `resolved` for #2841, #2745a, #2745b, 3a07c2eaa and e438816e3, and `refused` for #2834 and 5bf232eac.
  - `cmp -s` of each merged file between the two heads printed `SAME` for all seven.
  - None of the seven has both sides bump the stamp, so the guard change cannot reach them.

## Figures

- **The finder's harness** is round 1's `ev/reviewer-instruments/` on `probe/rev-3066-e2ba7157` (`adv.py`, `adv2.py`, `m3probe.py`, `cmrun.py`, `mut.py`, `replay.sh`), run unchanged at `5a08ec2e9` (a detached worktree) and at this head.
  - `adv.py`: 17 lines ` OK`, 0 `FAIL` at both ends. `diff` of the two full outputs exits 0 (`&& echo` printed `ADV OUTPUT IDENTICAL BOTH ENDS`).
  - `adv2.py`: `RESULT D2c may_drift_error: None` at both ends.
  - `m3probe.py`: `RESULT theirs-deleted alpha: ['beta', 'gamma']` at both ends.
  - `cmrun.py`: `ALL 30 CM PASSED` at `5a08ec2e9`, `ALL 31 CM PASSED` here.
  - The round-2 reviewer's `stamp_probe.py` (`verdict/3066`, `evidence/reviewer-instruments/`): see `## Null control`.
- **Stamp class.** `grep -nE "CLAIM_VERSION_MARKER|_parse_claims\(" tests/env_drift.py` is the round-2 reviewer's enumeration of every place the stamp is read or compared. Each site's disposition:
  - `merge_claim_decision`'s guard: closed in this diff. It is the S1 seam, now the two-sided comparison.
  - `_marker_key`, `_marker_blocks`, `merge_marker_decision` and `merge_claim_file`'s marker refusal: already the per-key rule (round 2).
  - `merge_claim_defect`'s stamp and marker-block equality: already exact both ways (round 2).
  - `merge_claim_refusal`: names the three stamps. Its "different" wording is now true whenever it prints.
  - `_parse_claims`: the reader, keyed by the same predicate as `_marker_key`.

  No returned site is undispositioned.
- **Census.** `python3 dev/audit/harnesses/claim_merge_census.py <driver-ref>` counts, per recorded merge, each side's changed scenarios against the merge base and their differing overlap.
  - Driver `f4a5082a6`: `RESULT resolved=0`, `RESULT refused=7`. Driver `2b6bef745`: the same.
  - Driver `b1a0be47d` and this head: `resolved=5`, `refused=2`, `hand_same=1`, `hand_differs=1`.
  - Per-row ours/theirs/overlap at this head (re-derived, the figure round 2 did not): #2841 5/1/0, #2745a 41/1/0, #2745b 41/5/0, #2834 5/5/5, 3a07c2eaa 3/1/0, e438816e3 4/41/0, 5bf232eac 45/50/42.
  - Null control: the same census over two planted pairs gave `ours=0 theirs=0 overlap=0`. One pair is the #2841 merge base against itself, the other `11e8075d` against itself.
  - The anchored census prints the same lines as round 2's copy when run from the root (`diff` exits 0, `&& echo` printed `NEW_EQ_OLD_FROM_ROOT`). Run from `/`, it completes, where round 2's copy raised `CalledProcessError` on `git show`.
- **Round 2's failing-first figure, re-derived.** The CM section of `5a08ec2e9`'s `tests/entities.py`, with `b1a0be47d`'s `tests/env_drift.py` in place, gave `8 of 30 CM FAILED`. The eight are the eight round 2 named. Null control: the same runner with `5a08ec2e9`'s own driver gave `ALL 30 CM PASSED`.
- **`tests/harness_headers.py`**: see Round-2 finding 1.
- **Scoped gate.** `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` (merge base `f4a5082a6`, three-dot) printed `MODE: SCOPED -- 7 script(s) run, 26 scoped out.` Its `scope.run`: `tests/entities.py`, `tests/env_drift.py`, `tests/golden.py`, `tests/harness_headers.py`, `tests/plan_view.py`, `tests/card.mjs`, `tests/card_drift.mjs`. Each ran with `PYTHONPATH=tests/hastub`, with `GOLDEN_MODE=drift` against the merge base for `golden.py`, alongside the `run_always` lines (`env_drift.py --claims-only`, `closure.py selftest`, `layout.py`, `harness_headers.py`):
  - `tests/entities.py`: `ALL 2514 ENTITY CHECKS PASSED`
  - `tests/env_drift.py`: rc=0
  - `tests/golden.py`: `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`
  - `tests/plan_view.py`: rc=0
  - `tests/card.mjs`: `ALL CARD CHECKS PASSED`
  - `tests/card_drift.mjs`: `card_drift: identical in all 45 states`
  - `tests/env_drift.py --claims-only f4a5082a6...`: `claims hygiene: ... ok`
  - `tests/closure.py selftest`: `ALL 117 closure shrink pins PASSED`
  - `tests/layout.py`: `layout self-test: ok`
- **`python3 tests/structure.py`**: `STRUCTURE RATCHET PASSED`.
- **`PYTHONPATH=tests/hastub python3 tests/env_drift.py --all f4a5082a666fcffc4968ed6bc540a6ab3e267c63`**: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE: 56 committed fixture(s) still match`, rc=0.
- **Claim files.** `git diff --quiet f4a5082a666fcffc4968ed6bc540a6ab3e267c63 HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo "CLAIM FILES BYTE-IDENTICAL"` printed `CLAIM FILES BYTE-IDENTICAL`.
- **Version files.** The same `git diff --quiet` over `VERSION`, `custom_components/heatpump_optimizer/manifest.json` and `RELEASE_NOTES.md`, with `&& echo`, printed `VERSION MANIFEST NOTES UNTOUCHED`.
- **Policy.** `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok: every generated rule is the generated form of its source`. In `--budgets`, `.claude/rules/claim-files.md` is 53 lines against its 53 cap, the same line count as round 2's text.
- **CI predict.** `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`: `CI PREDICT: no closures, fast, governance or instrument red predicted against f4a5082a666f (a data-file read is not seen)`. `git status --short` is empty after it.
- **prepr.** `bash tools/pr/prepr.sh <this body>`, run with no `PREPR_SKIP_CLOSURES`: `PRE-PR: 76cd77cb007ddbd0351d3a27596cadfbdef02439 00000000000000000000000000000 rc=0`. Its `pr-body` step printed `PR-BODY: 0 error(s)`. Its `closures` step printed `skip ... the diff cannot be scoped, so CI re-records every closure; a full derive here is forbidden`: that is prepr's own rule, not a skip I set.
- **Main did not move.** `origin/main` was `6421fe135` at that run and again before the handoff push, so no second run was owed.

## Architecture score

`python3 tools/audit/archscore/score.py --diff f4a5082a666fcffc4968ed6bc540a6ab3e267c63`: `Architecture score: dS +0.0000 NULL`.

## Red checks

Every check that went red at the reviewed head `5a08ec2e9`:

- **`tests / fast (3.14)`.**
  - Cause: the depth root `parents[3]` in this PR's new `dev/audit/harnesses/claim_merge_mutants.py`, which `tests/harness_headers.py` refuses. This diff caused it, and `a6c237fc2` fixes it.
  - Cheaper detector: `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`, about 2 minutes (2m17s here). It is one of the 7 scripts the scoped gate selects, and it was run before this handoff (`ALL 112 HARNESS HEADER CHECKS PASSED`).
- **`governance / instrument-self-tests`.**
  - Cause: the `pr_args` self-test's symlinked `unrelated-sleep` fixture. ubuntu-26.04 runners ship uutils coreutils, whose multicall `sleep` refuses the name. This is main's red, not this diff's, as main's own run 41294924835 shows. R10-HOTFIX-UUTILS-SLEEP fixes it.
  - Cheaper detector: none exists off the runner. This container's `sleep` is `GNU coreutils 9.4`, which runs under any name, so the fixture passes here. The red appears only where the runner image supplies the uutils multicall binary.
- **`pr-contract / pr-contract` and `gate`.**
  - Cause: the two reds above, plus round 2's stale `## Red checks` ("none ... no CI run yet"). `pr-contract` refused it with `PR-BODY: 2 error(s)`, and `gate` aggregates the rest.
  - Cheaper detector: `prepr.sh`'s body check (`tools/pr/prepr.sh --body-check`, which `body_push.sh` runs). It was run on this body before the handoff.

## Forward-carry

- Carry 3 (P214): the merge-main bot should relay `merge_claim_refusal`'s text, which names each refused scenario, fixture or stamp with both sides' lines. It waits on its own `edit-brief` taking `tools/pr/merge_main_bot.py` into this group's `files`, and stays on the roster as written. Carry: R10-996-RUNNER-CLAIMS
- Round 2's finding S1 (the three-way stamp guard) is fixed in this PR, not carried. It is pinned by `claims both sides changed under one stamp both bumped resolve per scenario`. Carry: dismissed: fixed in this PR
- Round 2's finding that the body had no `prepr.sh` line is answered under `## Figures`. Carry: dismissed: fixed in this PR

## Friction

- claim-files.md: contradiction: carry 2 (P209, s6-batch39) keeps "the refusal for a deletion" while carry 1 (P196, s6-batch34) rules that a scenario one side deleted and the other left alone stays deleted. Resolved here by P196's rule, since P209's stated reason (a union reinstates the deletion) does not hold for a three-way merge. Carry: dismissed: resolved in this PR's driver and pinned by `a claim one side deleted and the other left alone stays deleted`
