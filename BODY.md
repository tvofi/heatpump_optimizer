R10-RCA-GATE-BUSY-DEFER-2, the carries part (topic r10-rca-gate-busy-defer-p5): the root-cause addendum for the failure modes #3287 (`5c1fa41fb`) introduced as this class's countermeasure. Part 1 merged as #3278. Part of #201. This seat edits nothing in `tools/ci/` and no reader of the gate conclusion. The analysis is `dev/audit/rca/r10-gate-defer-read-final.md`, indexed in `dev/audit/config/bugclasses.json` as `_rca.R10-RCA-GATE-DEFER-READ-FINAL`.

- **Cause 1, the reader window.** #3287 made a red on the required `gate` check provisional: gate.py's `deferral()` red is published at once, and `settle` re-judges it later. No step enumerated that conclusion's readers. Five still take the red as final at origin/main `73365699a`, four in code and one in policy: `merge_train.py` `policy_refusal` (the BRANCH-POLICY park), `orchestrator_tick.py` `one_pr`/`main`, `review_packet.py` `gate_digest`, `merge_pr.sh` and `nudge.md` step 15. Process state (a): fixer step 8's `agreement.mjs` rule fires on a change to a reader, never to a writer. The countermeasure is P436's barrier on R10-HOTFIX-TRAIN-DEFER-WAIT, which has not landed.
- **Cause 2, the settle loop (finding, carried).** `sweep.py` `undecided()` counts the skipped jobs that a job re-run re-stamps. So `settle` re-runs two red gates at one head in turn, up to `ATTEMPT_CAP`, even on content reds. #3274's three runs reached attempt 44. Process state (c).
- **Carry 0:** covered by `5c1fa41fb`, with figures below.

## Carries

- Carry 0: covered by `5c1fa41fb`. The deciding gate's conclusion re-judges every deferring gate at the head without a human.
  - Census: `at_once_lag_min_max_decider_success=1.5` (every at-once deferral red whose deciders succeeded was green within 1.5 min), `residual_red_decider_success=0`, `at_once_green_by_human=6`.
  - Four of those six are hand re-runs at lag 0.0 racing the sweep. Two follow a cancelled or failed decider, which the sweep rightly leaves red.
  - The proving test in the tree is `tools/ci/sweep_selftest.py`'s settle census (#3287).
  - Measure asked for: 86 deferral reds on 43 heads, 2.0 per head that carries one. Decider-to-green: median 0.0 min under both programs; max 1.5 min (at-once) after a successful decider.
- Carry 1 (items 39f0a86e), and Carry 2, the same item written twice:
  - §1 of `dev/audit/rca/r10-gate-busy-defer-2.md` is corrected in this diff. "In #3261, the higher gate waits one poll" is bound to #3246's program, the one it replays, and #3287's at-once deferral is stated after it.
  - The document's `census` arm reads `gh api`, which this seat does not have. It was not run. The same question (gates judged by a program without the fix, after the fix merged) is measured with this PR's census instead: `stale_pin_reds_after_fix=6`, `stale_pin_reruns_after_fix=2` (#3291 d5f8f410, attempts 3 of two runs).
  - §5.2 stays needed. It is being built on `handoff-wip/r10-hotfix-gate-busy-defer-p5` (`a5ee73e39`, not merged), so it waits on that group.
- Carry 3: the addendum owed at the third instance is delivered.
  - Cause: RCA section 2.
  - Process state with evidence, including why #3287's review did not enumerate the readers: section 3.
  - Cost test with numbers: section 5.
  - Countermeasure: section 6, the R10-HOTFIX-TRAIN-DEFER-WAIT barrier from P436.
  - The barrier has not landed at `73365699a`, so the class is not yet recorded as barriered in `bugclasses.json`. The `_rca` entry carries it as `proposed`, and the class record waits on the barrier.

## Head

`aca864bce91258fb85d14ae7eba75075132e13b5`, branch `handoff/r10-rca-gate-busy-defer-p5`, cut from origin/main `73365699a`. origin/main was `73365699a` at the clean `tools/pr/prepr.sh` run (PRE-PR rc=0 at this head, 5 min 11 s) and at the re-read at 2026-11-08T08:00Z (`git merge-tree --write-tree origin/main HEAD`: no conflict). By the owner ruling of 2026-11-07, no merge of a moved main is owed. The three-dot diff:
- adds the harness, its fixture and its mutant spec;
- adds the RCA document;
- edits #3278's document (§1 and its Carries);
- adds the `_rca` entry;
- adds the harness's `tests/closures.json` INERT READS entry.

## Mutation proof

This PR adds no production line. It adds two detectors, and each is proven against real program copies and its own perturbation.

- **`loop`.** It replays #3274's recorded loop through `sweep.undecided()`.
  - At `73365699a` (and at `5c1fa41fb`, and at `d23377e1d` on the sibling branch) it predicts 129 of 129 actual re-runs.
  - Perturbation: with every `skipped` job dropped, it predicts 38.
  - The arm cannot run at `5c1fa41fb^1`, which has no `undecided()`. The settle, and so the loop, arrived with #3287.
- **`census`.** It separates a deferral red from any other gate red. With every deferral line erased, the fixture scores 0 deferral reds (the `selftest` arm's first null control).
- **`selftest` under a mutant.** Widening the scored conclusion from `failure` to `failure` or `cancelled` prints `FAIL non_deferral_reds: want 276, got 331` and `SELFTEST FAIL`. The unmutated harness prints `SELFTEST ok: 18 expected result(s), 2 null controls`.
- **#3278's replay arm** exits 0 at `812bb8747` and 1 at `73365699a`. It reads `C3-AT-ONCE` on all three c3 scenes, #3287's design.
- **Diff mutants.** With MUTANT_CMD set to this harness's `selftest`, `prepr.sh`'s step reads `no survivor` over 0 mutants. `mutant_run.py --diff` skips `dev/` (`SKIP_PREFIXES`), and every added Python line here is under `dev/audit/harnesses/`. Its wall time: 0.065 s.
- **Spec mutants instead.** `python3 -I tools/audit/seat/mutant_run.py --spec dev/audit/harnesses/r10_gate_defer_read_final_mutants.json --cmd "env GIT_DIR=<repo>/.git python3 -I dev/audit/harnesses/r10_gate_defer_read_final.py selftest"`.
  - 15 mutants on the harness's rule predicates: the scored conclusion, the program split, green-after-red, earliest green, same head, attempt end, the loop's skipped filter and time cut, stale pins, residuals, the lag filter, the null control, bot actors.
  - Wall 5.5 s. NULL survived; 14 KILLED; 1 survivor: M3-green-after-red.
  - M3 (`t > done` to `t >= done`) is equivalent on the recorded data: no `gate` success completes in the same second as a deferral red at its head.
  - The first pass had 6 survivors (M3, M5, M6, M10, M11, M15). Pinning the figures they move in the header's EXPECTED RESULT block (18 results now) killed five of them. The commit subject `aca864bc`^ says six; five is the count.

## Null control

- 276 gate failures that are not deferrals (`non_deferral_reds`) are never scored as deferral reds. A census keyed on `conclusion == failure` alone would count 362.
- Every residual deferral red (18) had a cancelled or failed decider (`residual_red_decider_success=0`). The sweep left no red standing behind a decider that succeeded.
- `loop` with the re-stamped skipped jobs dropped predicts 38, not 129. The 38 come from `undecided()`'s third arm (overlapping re-run gates), which only the loop produces.
- #3278's replay at `812bb8747` exits 0 on the same fixture where `73365699a` exits 1.

## Figures

- Census: `python3 dev/audit/harnesses/r10_gate_defer_read_final.py census`.
  - Totals: `deferral_reds=86`, `heads_with_deferral=43`, `prs_with_deferral=13`, `non_deferral_reds=276`, `residual_red=18`, `residual_red_decider_success=0`, `stale_pin_reds_after_fix=6`, `stale_pin_reruns_after_fix=2`.
  - Waiting program: `waiting_reds=45` on `waiting_heads=25`; red window median 31.0 / max 142.8 min; lag max 122.2 min, 0.0 min after a successful decider; `waiting_green_by_human=15`.
  - At-once program: `at_once_reds=41` on `at_once_heads=18`; red window median 32.2 / max 54.0 min; lag max 35.9 min, 1.5 min after a successful decider; `at_once_green_by_human=6`.
  - Loop cost: `bot_reran_content_reds=257`, `bot_reran_content_red_gate_min=159`, `bot_reran_content_red_prs=6`.
  - Rules: the harness docstring. A deferral red is a failed `gate` attempt with gate.py's `deferral()` line. The program is read from the `programs restored from` sha against `5c1fa41fb`. Green is the earliest `gate` success at the same head in any run.
- Per pull request: `python3 dev/audit/harnesses/r10_gate_defer_read_final.py heads`.
- Loop replay: `python3 -I dev/audit/harnesses/r10_gate_defer_read_final.py loop` prints `reruns=129 predicted_listed=129 predicted_without_skipped=38`. With `--ci <export>/tools/ci` for `git archive 5c1fa41fb tools/ci` and for `git archive d23377e1d tools/ci`, it prints the same.
- Self-test: `python3 -I dev/audit/harnesses/r10_gate_defer_read_final.py selftest` prints `SELFTEST ok: 18 expected result(s), 2 null controls`.
- Fixture: `dev/audit/harnesses/r10_gate_defer_read_final.json`, sha1 91154dda3fa995a445fe459896f0dc9bd11cfadb (`sha1sum`).
  - Coverage: every `ci.yml` run on the 13 pull requests created 2026-11-07T00:00Z to 2026-11-08T07:00Z, with jobs (`filter=all`) of every re-run or non-success run, and the log line of every failed gate attempt.
  - Recorded through the GitHub MCP tools: REST `actions/workflows/ci.yml/runs?branch=`, `actions/runs/<id>/jobs`, `actions/jobs/<id>/logs`.
  - #3304 was still looping during the recording. Its later attempts are not in the fixture.
- #3278's replay: `python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci <export>/tools/ci`, with `<export>` from `git archive <sha> tools/ci tools/pr`. rc 0 at `812bb8747`; rc 1 at `73365699a` and at `5c1fa41fb` (`defects=yes`, the three c3 scenes `C3-AT-ONCE`, naps 0).
- Ancestry: `git merge-base --is-ancestor cb24224b2 5c1fa41fb^2` exits 1, so #3287's head lacked #3278.
- Reader enumeration (fixer step 8; no in-tree instrument enumerates the readers of the gate conclusion).
  - Rule: the `git ls-files tools .github | … | xargs grep -nE …` command in RCA section 4. It returns 56 (file, function) sites; each was read.
  - Every seam that reads the `gate` context is dispositioned in section 4's table:
    - already guarded by #3290: `classify_cmd`/`classify_at` and the merge step's wait, `proof_watch.py`, `ci-watch.sh`, `bus.sh` dispatch, `postmerge.py`, `cloud_dispatch.py`;
    - open, to P436's barrier: `policy_refusal`, `orchestrator_tick.py` `one_pr`/`main`, `review_packet.py` `gate_digest`, `merge_pr.sh`;
    - open, policy, the owner's: `nudge.md` step 15;
    - not a reader: `prepr.sh`, `body_patch.sh`, `pr-contract.yml`.
- Ledger: `python3 tools/audit/fold_ledger.py check` prints `0 violation(s)`, 138 rca entries.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `python3 tools/pr/ci_predict.py` predicts no red after `--apply-inert`.

## Red checks

none: no pull request exists for this head yet, so no check has concluded. The orchestrator opens it.

## Forward-carry

- Cause 2, the settle loop, to the owner of `tools/ci/sweep.py`.
  - Fix: `settle` re-runs only a deferral red, or `undecided()` ignores `skipped` jobs and the overlap of the sweep's own re-runs.
  - Failing test first: this PR's `loop` arm reads `predicted_listed=0` for #3274's content reds. Null control: the census's at-once deferral reds are still re-run once their decider ends.
  - An open pull request whose runs sit at attempt 44 needs a fresh dispatched run, not a re-run: #3274's three runs at 4f8ab965 are past the sweep (`must_rerun`).
  - RCA sections 2, 5 and 6. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Cause 1's open readers, to P436's barrier group: `merge_train.py` `policy_refusal`, `orchestrator_tick.py` `one_pr`/`main`, `review_packet.py` `gate_digest` and `merge_pr.sh`, with the #3264 review instance (red 02:01:18Z, sibling green 02:01:51Z) as its failing case. Once it lands, record the class "a provisional gate red read as final" in `dev/audit/config/bugclasses.json` as barriered (RCA section 7). Carry: R10-HOTFIX-TRAIN-DEFER-WAIT
- Two policy items for the owner, routed to the orchestrator (RCA sections 4 and 6):
  - `nudge.md` step 15's raw reading of a gate failure;
  - extending fixer step 8's reader rule to a writer that changes a conclusion's meaning.
  - Also retire the hand re-run: the sweep greens a successful decider's head within 1.5 min, and a person's re-run raced it four times in the census.
  - Carry: #201

## Friction

- PROMPT.md: contradiction: `r10_rca_gate_busy_defer_2.py census`, which Carries 1 and 2 name for the re-measure, reads `gh api`, and this cloud seat has GitHub MCP tools and no `gh` for anything but search. The re-measure was done with a fixture recorded through MCP and an offline census, and the denominator of 55 PRs could not be re-taken. Carry: #201
- frugal-routing-hook: cost: the inline-search budget of 5 per prompt pushed the run recording and the reader enumeration into subagents, about 1.5 M subagent tokens for the three recording seats. Carry: dismissed: seat-harness configuration, outside this repository
