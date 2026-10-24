R10-STRUCTURE-ALIAS: `seam_cut_total` priced cross-seam attribute-reference **occurrences**, so a local alias of a repeated read paid for itself (O19, `prices = self._prices` in `_raise_cop_issue`, -2), and so did a bare getter returning a tuple of state reads (`_cop_state()`, -2; one edge in place of k reads pays 2(k-1)). Neither moves anything. The roster lists no issue under `fixes`.

What `seam_metrics` in `tests/structure.py` now prices:
- **Distinct pairs.** The cut is each (seam, attribute) pair and each (seam, callee) pair that crosses a seam boundary, counted once however often it is read. That is what an extraction has to make explicit, so rebinding a read inside one seam (an alias, tuple unpacking, a walrus) buys nothing, whatever its spelling.
- **A call of a bare state getter is priced as the reads it returns, at the caller**, not as one edge. `state_getter_reads` is the rule. A bare getter's body is a docstring, state-root aliases, and one `return` of a state read, or of a tuple, list, set or dict of state reads.
- **A `@property` read is a call.** Before this change a property read from another seam cost nothing, because the attribute branch skips method names and the call branch needs an `ast.Call`.
- **Every def of a name is its unit**, so a later `@<name>.setter` can no longer hide the getter's body or its getter shape.

Design choices the checks encode (`fixer.md` step 11):
- Call pairs are deduplicated as well as attribute pairs. If attributes were distinct and calls were occurrences, inlining a repeated cross-seam call into raw reads would pay.
- A callee that computes, or that returns a constructed value, stays one call edge. That is the narrowed interface the metric should keep rewarding, and the `computing` self-check pins it.
- The evidence-only line `internal call occurrences` now includes property reads: 367 at the base, 380 at the head. It is not budgeted.

Alternatives considered (`fixer.md` step 17):
- **Refuse a bare getter.** The step-8 census returns 5 bare getters already in the coordinator. They are properties: `prices`, `mode`, `dhw_temperature`, `system_identification_active` and `_price_model`. Refusing them would force deleting or bloating working properties to fit the instrument.
- **Keep occurrences and resolve aliases.** Charging every load of a local bound to a state attribute means enumerating spellings (assignment, tuple unpacking, walrus, for-target, comprehension). That is the #1874 shape. Distinct pairs close the class without a list.

## Head

ddadd4d4eda57c7ce78701d4615423f88c995403 (code head `handoff/r10-structure-alias`), on origin/main `e8a08cf9efefc96c36e79efa7459562e27007b54`, which is also the merge base. The branch was cut at `145bfe197` and `origin/main` was merged in at `ddadd4d4e` before the handoff; every figure below was re-taken after that merge (gate run 2026-10-24T11:23Z-11:55Z, `date -u`). Every figure was taken at this head unless it names the merge base.

## Mutation proof

Each mutant was applied to `tests/structure.py` in place at the head and restored after (run after the merge of main). `PYTHONPATH=tests/hastub python3 tests/structure.py` was run for each, with the red lines pasted:
- M1, no getter see-through (`getters` left empty): rc=1, `FAIL  a getter returning bare state reads is priced as those reads at its caller`.
- M2, property branch disabled: rc=1, the getter check plus `FAIL  a property is a callee: read from another seam, it is priced as a call`.
- M3, occurrences restored (the attribute sets back to lists, `inside`/`outside` counted per occurrence): rc=1, `FAIL  a second read of an attribute, or a local alias of it, costs nothing more (O19)` and `FAIL  a helper is priced as the method it was cut from (#1686)`.
- M4, the getter shape read from a name's last def: rc=1, the getter check and the property check.
- M5, no dict branch in `state_getter_reads`: rc=1, the getter check.
- M6, a unit made of only its last def: rc=1, `FAIL  a property's setter hides none of its getter's reads`.
- M7, a non-read element accepted in a getter's return: rc=1, `FAIL  a callee that computes is a call edge, not the state it reads`.
- M8, any statement accepted before a getter's return: rc=1, the same computing check.

Failing test first: the alias and getter self-checks were written before the fix. At the base's `seam_metrics` they read `FAIL  a second read of an attribute, or a local alias of it, costs nothing more (O19)` and `FAIL  a getter returning bare state reads is priced as those reads at its caller`. The property and setter checks were each written red before their branch.

## Null control

- **The finder's plants at the merge base.** `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_structure_alias.py`, run from a worktree of the merge base `e8a08cf9e` with the harness copied in (sha1 `a4461ca3839b996db00e564cb7425e29ab69e7e4`). It reads `clean_seam_cut_total=710`, `alias_seam_cut_total=708` and `getter_seam_cut_total=708`. At the head the same command reads 313, 313 and 313. The plants are the null control for the fix: each moves the figure on the unfixed instrument, and neither moves it on the fixed one.
- **The finder's own diffs.** `ev/plant_p2.diff` from `probe/rev-2620-654004be` still applies at main with an offset. `ev/plant_p3.diff` does not, because `_cop_watch` has left main. It was re-anchored to the same edit (the getter in `learning`, `_scores_view` reading through it, plus its `seam_map.json` entry). With each diff applied, `python3 tests/structure.py` read `seam_cut_total` 708 at `145bfe197` and 313 at the pre-merge head `0fd39b403`; the in-memory replay above is the post-merge re-take. The only other rows that fail are `class_excess_loc` and `max_class_loc`, by the lines the plants add (+1 and +4), at both ends.
- **The see-through is not blanket.** The `computing` self-check holds at both ends. A callee that computes (`return self._depth + self._limit`, `return self._depth, len(self._limit)`, or a store before the return) costs one call pair, not the reads.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `seam_cut_total` is re-recorded 710 -> 313 by `--record`, with `recorded_at` at the branch's cut point `145bfe197`, an ancestor of main; no other row moves (`git diff origin/main...HEAD -- tests/structure_budgets.json`), and the merge of main brought in main's own `class_excess_loc` and `max_class_loc` re-record unchanged. The reason is in commit `4c870ee10`'s message (CLAUDE.md rule 2). This is a downward re-record from a counting-rule change, not a raise.
- Seam table, `python3 tests/structure.py` (its "coordinator seam table" block), cut per seam, base -> head: dhw 68 -> 27, learning 283 -> 104, fetch 94 -> 47, grid 155 -> 67, views 110 -> 68.
- Finder harness: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_structure_alias.py`. Its numbers are under `## Null control`.
- Class seams (`fixer.md` step 8). The rule is the same harness's census: every coordinator unit `state_getter_reads` accepts, and every `@property` read from a seam other than its own (`RESULT bare_getters`, `RESULT properties_read_cross_seam`). At the head it returns 5 getters and 3 cross-seam properties. Each one's disposition:
  - `_price_model` (fetch, read from dhw, grid and learning): closed here. It is now priced as those seams' reads of `_price_learner`; before, it cost 0.
  - `effective_config` (core, read from fetch and grid) and `target_temperature` (core, read from learning): closed here. Each is now a call pair; before, each cost 0.
  - `prices`, `mode`, `dhw_temperature` and `system_identification_active`: not applicable. The census finds no coordinator unit in another seam reading them, so the seam cut has nothing to price for them.
  - Alias spellings: closed by construction. Distinct pairs make any within-seam rebinding free of effect; self-check `a second read of an attribute, or a local alias of it, costs nothing more (O19)`.
  - At the merge base the census has no rule to run (`# census: this tree's structure.py has no bare-getter rule`). That is the class this diff closes.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 8 script(s) run, 25 scoped out`. With `PYTHONPATH=tests/hastub` at the head:
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `tests/features.py`: `ALL 4356 FEATURE CHECKS PASSED`.
  - `tests/doc_claims.py`: `ALL 203 checks PASSED`.
  - `tests/arch_score.py`: `ALL 255 ARCHITECTURE SCORE CHECKS PASSED`.
  - `tests/arch_score_head.py`: `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`.
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `tests/entities.py`: `2 of 2425 ENTITY CHECKS FAILED`, both `hb:positive_control` on its final try (`py-spy rc=0 names it: False`; one sample `TimeoutExpired ... after 0.5 seconds`). The pre-merge base `145bfe197`, run from its own worktree, reads the same `2 of 2425 ENTITY CHECKS FAILED` with the same two `try 3 of 3` lines. That is this seat's py-spy sampling the heartbeat lane's spin, not this diff, which touches no file the lane runs.
  - The `run_always` set: `tests/layout.py` `layout self-test: ok`; `tests/closure.py selftest` `ALL 117 closure shrink pins PASSED`; `tests/env_drift.py --claims-only e8a08cf9efefc96c36e79efa7459562e27007b54` `claims hygiene: ... ok`.
  - `tests/stress.py` is left to CI's required mutation check (`fixer.md` step 5).
  - `python3 -I tools/audit/seat/tmp_paths.py --check` reads `0 refused`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` reads `no closures or fast red predicted`. It predicted an INERT READS entry for the new harness, repaired before the handoff with `--apply-inert` (commit `fb13363ee`). `tests/harness_headers.py` then refused the harness's fixed-depth root (`depth seams: ... parents[3]`); it uses the canonical `repo_root` walk from commit `0fd39b403`.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL`. No production line changed, and the score does not read `seam_cut_total`: `tools/audit/archscore/vector.py` stubs `seam_metrics`.

## Red checks

none: no CI has run on this ref. The one predicted red, INERT READS for the new harness, was repaired before the handoff. The local `hb:positive_control` red under `## Figures` reproduces at the merge base, so it is not this branch's.

## Forward-carry

none. The roster's only group carrying `seam_cut_total` or O19 is this one: a grep of `dev/programme/rosters/wave-r10-groups.json` on `origin/handoff/audit-r10-roster` returns only R10-STRUCTURE-ALIAS. Every later stage derives the metric at its own merge base, so no figure needs carrying. A branch in flight that re-recorded `seam_cut_total` under the occurrence rule will conflict on `tests/structure_budgets.json` and re-records it at its merge with main. That is a merge mechanic, not a finding.

## Friction

none
