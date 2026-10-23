Fix review: merge 72fbab2a719ce14870aa3284a35d043ea1b9588d

bus-nonce: 654004be88378fbedacb0dc55dea4c83

Round: 3. Round 2 blocked 08ba3d9d7 as metric-gamed (probe/rev-2620-62684c0b). This is the first review of the re-cut payment. Under fix-review.md's closing line, this is not yet the fourth round.
Roles contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the copy is current. Merge base is c26499e01, which is origin/main at review.

## Verdict

The payment is a real move, not an alias. Every new mutation site is pinned and killed. The finder's harness and null control hold at both ends. CI is green on this head apart from `nightly-status`, which grades main. The tree merges cleanly with origin/main.

## (a) seam_cut_total 708 -> 707 is earned

- **Measured.** `tests/structure.py` reads `seam_cut_total` 708, `class_excess_loc` 18268 and `max_class_loc` 8514 at base c26499e01. At the head it reads 707, 18257 and 8503, and prints `STRUCTURE RATCHET PASSED` (ev/structure_base.txt, ev/structure_head.txt). `tests/structure_budgets.json` moves only downward, to the measured values, so nothing is raised.
- **No alias in the diff.** No added production line binds `<local> = self.<attr>` (grep over the diff's added lines). The round-2 alias in `_raise_cop_issue` is gone: it reads `self.currency` twice, as at the base.
- **Remove the mechanism.** At the head I restored `_scores_view`'s inline reads of `self._cop_baseline` and `self._cop_health_cusum`, which is the base text, and kept `_cop_watch` for `_learning_view`. The result is `seam_cut_total 709 > 707 (+2)` and `class_excess_loc`/`max_class_loc` +6 (ev/plant_p1.diff, ev/structure_p1.txt). The whole -2 is the move, and the narrative's +1 is still paid by it.
- **Alias plant (O19).** At the head I planted `prices = self._prices` in `_raise_cop_issue`. That alone moves `seam_cut_total` to 705 (-2) with nothing improved (ev/plant_p2.diff, ev/structure_p2.txt). The instrument still counts occurrences, so the O19 carry stands and is live. This diff did not pay that way.
- **Plant of the diff's own kind (rule 14).** I wrapped the same two reads in a bare getter, `_cop_state()` in `learning`, which returns `(self._cop_baseline, self._cop_health_cusum)`, and left the count logic in `views`. That also reads 707 (ev/plant_p3.diff, ev/structure_p3.txt). The instrument therefore cannot tell a narrowed interface from a raw-state getter. The diff's change is not that shape:
  - `_cop_watch` returns derived values (the watched count and the clipped Cusum share), not state.
  - It deletes a duplicated count that had divergent guards (`_learning_view` had `np.isfinite` and `_scores_view` did not).
  - It shortens the class by 10 lines (11 with the one-line comment). Per rule 14 this is an instrument finding, not a block (see Findings).
- **Architecture score.** `score.py --diff c26499e01 HEAD` prints `Architecture score: dS +0.0000 NULL` (ev/archscore.txt). This is not a raise, so CLAUDE.md rule 2's raise payments do not apply. The score does not read the change as worse.
- **Behaviour.** The new `np.isfinite` guard in `_scores_view` only changes a NaN count. `_learned_pair` validates counts as int, and the BOOLOP mutant shows the guard is live in `_learning_view`'s path: the check `a non-finite aperture n does not wedge _learning_view` fails under BOOLOP.

## (b) The four _cop_watch sites at this head

At this head, line 9130 is `if np.isfinite(entry[1]) and int(entry[1]) >= COP_BASELINE_MIN_SAMPLES` and line 9132 is `return watched, float(np.clip(...))`. Four ledger files under `tests/mutation_ledger/killed_by/coordinator.py/` name `tests/features.py` as the killer: `_cop_watch.BOOLOP.bba11eeb`, `CMP_BOUND.bba11eeb`, `CLAMP_DROP.7eb4b17f` and `RETURN_DEL.7eb4b17f`.

Each mutant was run from a `git archive` copy of the head with `PYTHONPATH=tests/hastub tests/features.py`, using the /opt/hpo/venv-ci python 3.14 with numpy 2.4.6 (ev/mutant_*.diff, ev/features_mut_*.txt). The head itself prints `ALL 4310 FEATURE CHECKS PASSED` (ev/features_head.txt).

- **BOOLOP** (`and` -> `or`): `3 of 4310 FEATURE CHECKS FAILED`. Failures: `the machine grade starts at exactly COP_BASELINE_MIN_SAMPLES samples [{19: 100.0, 20: 100.0}]` and `a non-finite aperture n does not wedge _learning_view`.
- **CMP_BOUND** (`>=` -> `>`): `2 of 4310 FEATURE CHECKS FAILED`. Failure: `the machine grade starts at exactly COP_BASELINE_MIN_SAMPLES samples [{19: None, 20: None}]`. The new check drives a bucket at COP_BASELINE_MIN_SAMPLES-1 (19, expected None) and at exactly the bound (20, expected 100.0) through `_scores_view`, the production symbol.
- **CLAMP_DROP**: `2 of 4310 FEATURE CHECKS FAILED`. Failure: `a machine past the alarm threshold still grades 0, not below [-100.0]`.
- **RETURN_DEL** (`pass`): rc=1, with the D1-s2-51, D1-s2-91 and D1-s2-04 fence checks failing. The run then ends in `ConfigEntryNotReady: 'NoneType' object is not subscriptable`, so it is killed.
- **Runner artifact.** In every archive copy, `and the path that proceeds still stamps a resolvable recorded_at (#363)` also fails, as the body says. It passes in the git worktree at the head.
- **CI's mutation lane** (job 120262485090, ev/mutation_lane.txt): `PIN RE-VERIFICATION: 3 reproduced` covers CMP_BOUND, CLAMP_DROP and RETURN_DEL. It reports `0 survivor(s) of 3 evaluated`, both baselines `rc=0 failed=0`, and the null control survived. The green is therefore a real evaluation, not INCONCLUSIVE. The unpinned-site count is 4030, against 4034 at the base, so the diff's four sites are pinned.
- **Carried mutants.** Reverting `_narrative_view` to `resolve_currency(hass)` fails D14-s3-01 `[{'EUR/kWh': ['SEK'], 'SEK/kWh': ['SEK']}]`. Reverting `_raise_cop_issue` to `resolve_currency(self.hass)` fails the R10-CURRENCY COP-notice check with the same shape. With the alias gone, the COP-notice check still kills its mutant.

## (c) ci_predict and the body's sections

- **ci_predict.** At the head, `tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: no closures or fast red predicted against c26499e01f9d` and names no unpinned site (ev/ci_predict.txt).
- **`## Unpinned sites`** reads `none`.
- **`## Red checks`** against the head's check-runs (ev/check_runs.txt, every run concluded at 06:33Z):
  - The only red is `nightly-status`. It reports that no scheduled nightly on main has concluded yet. The diff does not reach what it reads, so it is not this PR's (fix-review.md 11), and it is not a required context.
  - `pr-contract` is green, including a run started at 06:33:52, after the last lane concluded. It was red in round 2, and the body answers that red with a cheaper detector: `carry_audit.py check --body`.
  - The body also answers the round-3b `mutation` red predicted by ci_predict, which is now fixed at the root with `--pin-killed`, and the local `structure.py` red.
  - The local `tests/entities.py` reds are py-spy heartbeat checks on the fixer's host. CI's `fast (3.14)` is green, so nothing is left unanswered.

## (d) Closing #2243 and #2222

**#2243 (class P8).** The issue lists four findings or instances, and each is closed:
- D12-s3-01, together with the two `_command_valve_target` sweep instances: closed by R10-FAHRENHEIT, #2285 merged at 19ff374e9, which is "Part of" this issue (`fixes: []`).
- D14-s3-01, with D14-s2-01 merged into it: closed by this PR.

The class enumerator `dev/audit/rounds/round10/D14/sweep-P8/p8_enumerate.py` reads `flagged=1 seams=11` at the base (`coordinator.py:10379 _narrative_view FLAG`) and `flagged=0 seams=10` at the head (ev/base_p8_enumerate.txt, ev/head_p8_enumerate.txt). The finder's harness at the head reads `base_mismatched_seams=0`. Closing #2243 is right.

**#2222 (class I5).** The other instances belong to R10-UX-SETUP, R10-I5-DOCS and R10-BRIEFS-FOLD, all at stage done, so this PR's D5-s3-01 is the last one. The issue's enumerator `sweep_i5.py` at the head shows every instance the issue tables as cleared:
- F1 = F2 = F4 = F5 = 0 (none printed).
- W3 = 0.
- F3 loses `money_currency` (base 7 -> head 6). That one line is the only base/head difference (ev/base_sweep_i5.txt, ev/head_sweep_i5.txt).

Closing #2222 is right. The six remaining F3 hits are new drift since the round-10 baseline, not #2222's instances (see Findings).

## (e) Footers

No repository rule governs commit footers (`git grep` over dev/governance, tools/pr, .claude, .github and CLAUDE.md finds none).
- This round's commits (0ebc7cf1e, c34bb23e9, 34bde2120, e60558413, f80d6125a, d5abe9de7, and merges 92478f062, 4731c08a4, 007ec1999, 72fbab2a7) carry no `Co-Authored-By`/`Claude-Session` trailers.
- The round-1/2 commits (701448f90, 23392d5d6, 08ba3d9d7) keep theirs. They remain ancestors of the head unchanged, so nothing was rewritten.
- Nothing here blocks.

## Other checks

- **Finder's harness and null control** (`dev/audit/rounds/round10/D14/s3/p8_replay_currency.py`, sha1 1acaac17…, the same at both ends; ev/harness_*.txt):
  - Base c26499e01: `base_mismatched_seams=1`, `clean_mismatched_seams=0`, `reintroduce_mismatched_seams=14`.
  - Head: `base_mismatched_seams=0`, `clean_mismatched_seams=0`, `reintroduce_mismatched_seams=14`.
  - The brief's carry holds: reintroduce is 14 and clean is 0 at both ends.
- **comment_symbols** (sha1 19dfe784…): `untriaged_missing` 7 -> 6. The only difference is the `money_currency` line. This matches the body's 7 -> 6, which the body took at f38f91852 and I re-took at c26499e01.
- **Pinned files untouched.** VERSION, manifest.json, RELEASE_NOTES.md and tests/golden have an empty three-dot diff, and no claim file is touched.
- **Merge.** `git merge-tree --write-tree origin/main 72fbab2a7` exits 0 (tree 23978102a) with no MERGE-CLAIM lines (ev/merge_tree.txt). #2647 has not landed, so the body's `seam_cut_total` conflict note does not apply yet.
- **Forward-carry (rule 10).** The body's structure-instrument carry is O19 on R10-CURRENCY at origin/handoff/audit-r10-roster. It states its control as a precondition: an alias planted on a clean tree must not move the figure, plus a mutant on the counting arm.
- **Body figures.**
  - "The coordinator class is 10 lines shorter": the move is -10, and the one-line `_raise_cop_issue` comment makes -11, which matches the budget rows.
  - The "4309 checks" the body quotes was at e60558413, before the bound check. The head has 4310.
- **R10-FEEDS carry.** The diff touches no `_get_current_price`/`_current_spot_price` caller.
- **Head at verdict.** I measured 72fbab2a719ce14870aa3284a35d043ea1b9588d, and `git ls-remote` shows it still at refs/heads/fix/r10-currency when this verdict was written (ev/HEAD.txt).

## Findings

- **The seam-cut instrument also rewards a raw-state getter.** `tests/structure.py`'s `seam_metrics` counts a `self.<method>()` call as one cross-seam edge. So replacing k cross-seam attribute reads with one call to a getter that returns the same state lowers `seam_cut_total` by 2(k-1), with nothing encapsulated. My `_cop_state()` plant gave -2. This is the same class as O19, the alias, by another route. O19's fix needs to cover it too: either count the distinct (seam, attribute) pairs reached through the callee, or refuse a callee whose only body is a tuple of state reads. Add a null control: a getter planted on a clean tree must not move the figure. Carry: R10-CURRENCY
- **sweep_i5 shows six new comment symbols missing at main** that #2222 did not list: `inputs.py:361` ATTR_MIN_TEMP/ATTR_MAX_TEMP, `optimizer.py:3528`, `plan_step.py:1`, `price_tiles.py:1` and `replay_doc.py:86`. They also show as `comment_symbols_untriaged_missing=6`. These came after the round-10 baseline, and the next D5 finder re-measures from its own baseline, so they do not keep #2222 open. Carry: dismissed: post-baseline drift, owned by the next audit round's D5 finder, which measures from its own baseline; not an instance of #2222's tabled set.
- **The class harnesses for D12-s3-01 and the valve sweep no longer run at main.**
  - `dev/audit/rounds/round10/D12/s3/surface_units.py` raises `AttributeError: pump_arbiter has no attribute 'state_unit'`.
  - `p8_valve_probe.py` raises `TypeError: cannot create weak reference to 'types.SimpleNamespace'` (ev/head_surface_units.txt, ev/head_p8_valve_probe.txt).
  - This diff touches neither code path. #2285 closed those instances, and P8's enumerator reads 0, so they are not this PR's.
  - Carry: dismissed: round-10 harness rot against #2285's merged code, outside this group's files; a harness owner re-cuts it if D12-s3-01 is re-audited.
- **Disclosure: the instruments are mine.** The structure plants (p1 to p3) and the mutant scripts are my own. Each is in ev/ as a diff against the head. The harnesses are the finder's, from dev/audit/rounds/round10, run unchanged from each tree.
