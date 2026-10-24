R10-STRUCTURE-ALIAS: `seam_cut_total` priced cross-seam attribute-reference **occurrences**, so a local alias of a repeated read paid for itself (O19, `prices = self._prices` in `_raise_cop_issue`, -2). A getter returning state reads paid as well (`_cop_state()`, -2; one edge in place of k reads pays 2(k-1)). Neither moves anything. The roster lists no issue under `fixes`.

Repair round 2. Fix review round 1 (`review/2711`, verdict on `5021b50de`) returned `blocked class-open`. Its finding was that `state_getter_reads` was a spelling enumeration: a docstring, root-alias assigns, and one `return` of a read or a display of reads. Five equivalent spellings of the O19 getter still paid -2: a leading `pass`, `tuple((a, b))`, `(a, b)[:]`, `dict(b=a, c=b)`, and a trailing `None`. The shape list is gone. A callee is now priced by **what escapes through its return value**, not by the form of its body.

What `seam_metrics` in `tests/structure.py` prices at this head:
- **Distinct pairs** (unchanged from round 1). The cut counts each (seam, attribute) pair and each (seam, callee) pair that crosses a seam boundary, once however often it is read. Rebinding a read inside one seam buys nothing.
- **What a value may hold: `StateFlow`.** Per unit, it follows state reads through locals, however they are bound (assign, annotated assign, augmented assign, walrus, for and comprehension targets, `with ... as`, nested `def`). It also follows them through displays, operators, subscripts, conditional expressions and lambdas. A call may hand back what it is handed, including its receiver and keyword arguments. A call may also store what it is handed into anything else it is handed: `out.append(self._x)`, `setattr(out, "x", ...)`. A unit call carries that callee's own escape set. A `yield` returns as surely as a `return`.
- **What cannot carry.** The rule lists only the forms that cannot hold an object: a comparison, a `not` and a formatted string (fresh bool or str), and constants (`_FRESH`). Any spelling nobody enumerated carries by default. That inverts the #1874 shape the review refused.
- **How a call is priced.** At the caller, a call costs the reads that escape through the callee's return. The (seam, callee) edge stays unless the callee is **transparent**: it reads only what it hands back, stores nothing, and calls only transparent callees. A callee that hands nothing back is the one edge it was. So is a callee that reads more than it returns or stores state, and the state it does return is read on top of the edge.
- **The coordinator handed back is the coordinator.** Reads through a value that may be the coordinator itself are state reads. That covers a callee returning `self`, `(self,)`, or an annotated `ctx: Any = getattr(self, "_ctx", self)`, and it covers `_ctx_of(self)._x`, which cost nothing at the merge base. An annotated alias of the state root is an alias and its `self._ctx` value a hop (`state_root_bindings`).
- A `@property` read is a call, and every def of a name is its unit (both unchanged from round 1).

Design choices the checks encode (`fixer.md` step 11):
- **Opaque calls carry conservatively.** `float(self._config.get(...))` and `self._a + self._b` are taken to hand back what they read. So a callee whose whole body computes from state it then returns is transparent and priced as those reads, not as one edge. This over-prices an honest one-attribute computation by nothing (one read and one edge cost the same 2). It never under-prices a getter, which is the direction the ratchet is gamed in.
- **An opaque call is not taken for the coordinator.** In `f(self).x`, the read of `x` is f's. The coordinator travels only through names, displays, subscripts, operators and unit calls. Taking every `f(self)` result for the coordinator charged method names on returned objects (`get`, `status`, `samples`) as state attributes.
- **A called function's own name holds nothing.** `dict(b=...)` does not bind its arguments into `dict`, so the keyword path is the one carrying them (M11 pins it).
- **Reads by computed name** (`getattr(self, name)`, `self.__dict__[k]`) are invisible to the cut in both trees. That is not a return-value seam, and this diff does not change it.

## Head

28987b7cef417bc1fce3dce115f1853c06706fa7 (code head `handoff/r10-structure-alias`), on the merge base `e97f5749b441b282e43bd99dbcbb762e9d10a369`, which was origin/main's tip throughout the measurement. Main moved to `73b69fe0a` at the push (2026-10-24, `git fetch`), after every figure was taken. The head is the PR head `5021b50de` with origin/main merged in (`c7949357b`), then this round's five commits. Every figure was taken at this head after that merge (2026-10-24T14:00Z-15:10Z, `date -u`). The exceptions are figures that name the merge base `e97f5749b` or the blocked head `5021b50de`.

## Mutation proof

The instrument is `$SCRATCH/mutants.py` (not committed). It applies each mutant to `tests/structure.py` in a detached worktree at the head, runs `PYTHONPATH=tests/hastub python3 tests/structure.py`, prints the FAIL lines, and restores the file. The predicate is mutated each time, never a tail:
- M0, no mutation (the runner's null control): rc=0.
- M1, transparency off (every call keeps its edge): rc=1. Red: `FAIL  a call is priced by what escapes through its return: a getter of k reads costs the k reads, however it is spelt (O19)` and `FAIL  a callee handing back the coordinator itself is read through: what the caller reads through it is its reads`.
- M2, what escapes is not read at the caller: rc=1. Red: the getter check and `FAIL  a callee that does more than hand back what it reads keeps its edge, and what escapes is read on top`.
- M3, an opaque call holds nothing it is handed: rc=1, the getter check.
- M4, `BinOp` added to `_FRESH`: rc=1, the getter check.
- M5, a subscript holds nothing of its container: rc=1, the getter check.
- M6, a call stores nothing into what else it is handed: rc=1, the getter check.
- M7, the coordinator itself carries nothing: rc=1. Red: `a read that crosses the seam costs one, however it is spelt`, the fresh-edge check, the does-more check, `a property's setter hides none of its getter's reads` and `a helper is priced as the method it was cut from (#1686)`.
- M8, transparency ignores reads not handed back: rc=1, the does-more check.
- M9, `Compare` removed from `_FRESH`: rc=1. Red: `FAIL  a callee handing back nothing of the state is the one edge it was` and the does-more check.
- M10, a `yield` is not a return: rc=1, the getter check.
- M11, an opaque call's keyword arguments not handed to it: rc=1, the getter check.
- M12, an annotated assign is not a root alias: rc=1. Red: `a read that crosses the seam costs one, however it is spelt` and `a read of what the seam owns costs nothing, however it is spelt`.

M11 and M12 survived their first run. M11 survived because a bare function name was being treated as a holder of its arguments, which made the keyword branch redundant. Commit `78d8fe6ed` drops that, and `1c882ad10` drops an unreachable keyword branch. M12 survived because no check spelt the annotated hop. `1c882ad10` adds `ctx: Any = self._ctx` to `SEAM_SELF_CHECK_SPELLINGS`. The list above is the re-run at the head.

Failing test first. The new self-checks were run against the `seam_metrics` of two other trees, by swapping it in under the head's checks (`$SCRATCH/ftf.py`):
- At the merge base: 7 red, including `a call is priced by what escapes through its return ... (O19)`, `a callee handing back the coordinator itself is read through ...` and `a read of what the seam owns costs nothing, however it is spelt`.
- At the blocked head `5021b50de`'s shape-list rule: 4 red. Three are the getter, root-getter and does-more checks; the fourth is the owned-spelling check, from the annotated hop.

## Null control

- **The finder's plants and the reviewer's spellings at both ends.** The command is `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_structure_alias.py` (sha1 at the head `0f6a9978a77e7cf8486009949fcf0f9a8756cfbf`). It plants the alias, the getter, the review's five spellings, and two more spellings of the same plant: `(a,) + (b,)` and a list built by `append`. At the merge base `e97f5749b`, with the harness copied in, it reads `clean_seam_cut_total=710` and every plant 708. At the head it reads `clean_seam_cut_total=367` and every plant 367. The review's own instrument (`review/2711:evidence/variants.py`) reads clean 710 / every variant 708 at the base, and clean 367 / every variant 367 at the head.
- **The finder's P2 diff applied with `patch`.** `probe/rev-2620-654004be:ev/plant_p2.diff` was applied to `coordinator.py` and `python3 tests/structure.py` was run. At the head the only FAIL rows are `class_excess_loc 18210 > 18209 (+1)` and `max_class_loc 8450 > 8449 (+1)`, with `seam_cut_total 367 <= 367`. At the merge base the same two rows fail by +1, and `seam_cut_total` reads 708, a gain of -2 against 710. `ev/plant_p3.diff` does not apply at either end because `_cop_watch` has left main. The harness re-anchors that plant to the same edit.
- **A callee that encapsulates stays priced as before.** The self-check `a callee handing back nothing of the state is the one edge it was` covers four such callees: `return self._depth > self._limit`, a formatted string, `return not (...)`, and reads then `return None`. Each costs exactly the one edge, which is not the direct-read cost. The does-more check gives the second null control: `return self._depth if self._limit else None`, and a store before the return, each cost the edge plus `_depth`.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - `seam_cut_total` is re-recorded 710 -> 367 by `--record` against main's table, with `recorded_at` the merge base `e97f5749b`. The reason is in commit `d73a3bf1f`'s message (CLAUDE.md rule 2).
  - No other row moves: `git diff origin/main...HEAD -- tests/structure_budgets.json` shows only `seam_cut_total` and `recorded_at`.
  - This is a downward re-record from a counting-rule change, not a raise.
  - Round 1's 313 was this metric under the shape list the review refused. The return-value rule also charges what that list let through: state handed back by callees that also compute or store, and reads through `_ctx_of`. So the head reads 367.
- Seam table, from `python3 tests/structure.py`'s "coordinator seam table" block. Cut per seam, merge base -> head:

  | seam | merge base | head |
  |---|---|---|
  | dhw | 68 | 30 |
  | learning | 283 | 119 |
  | fetch | 94 | 65 |
  | grid | 155 | 88 |
  | views | 110 | 65 |

  The evidence-only `internal call occurrences` line reads 367 at the base and 382 at the head; it is not budgeted.
- `seam_metrics` wall time on this seat's checkout is about 1.1 s, against about 0.1 s at the merge base. This is `StateFlow`'s fixed point over the units' escape sets. It is measured by timing one `seam_metrics` call from `python3 -c` and is not budgeted.
- Class seams (`fixer.md` step 8). The rule is the harness's census at the head:
  - It prints every coordinator unit whose return value may hold state, as `seam_metrics` reads it (`returned_state`): `RESULT units_returning_state=125`, of which `RESULT transparent_callees=76`.
  - Of those, `RESULT units_returning_coordinator=2`, the units whose return may be the coordinator itself.
  - It prints every call crossing a seam into one of them, by a syntactic over-approximation that names the unit as `.name` or `name(...)`: `RESULT cross_seam_calls_of_state_returners=68`.

  Dispositions:
  - All 68 crossing pairs: closed in this diff. Each is priced by the one rule: the reads escaping through its return are charged at the caller, and the edge stays unless the callee is transparent. No pair has a second path.
  - `coordinator._ctx_of` (core, transparent, holds `<state>`): closed here. Reads through it from `dhw`, `grid`, `learning` and `views` are now state reads; at the base they cost nothing.
  - `async_diagnose_interval` (core, holds `<state>`): the census finds no caller in another seam. Same-seam reads through its result are priced by the same rule.
  - The alias spellings: closed by construction. Distinct pairs make any within-seam rebinding free of effect (self-check `a second read of an attribute, or a local alias of it, costs nothing more (O19)`). The annotated alias is now a spelling in `SEAM_SELF_CHECK_SPELLINGS`.
  - At the merge base the census has no rule to run (`# census: this tree's structure.py prices no callee by its return value`). That is the class this diff closes.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 8 script(s) run, 25 scoped out`. Each was run at the head with `PYTHONPATH=tests/hastub`:
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `tests/features.py`: `ALL 4356 FEATURE CHECKS PASSED`.
  - `tests/doc_claims.py`: `ALL 203 checks PASSED`.
  - `tests/arch_score.py`: `ALL 255 ARCHITECTURE SCORE CHECKS PASSED`.
  - `tests/arch_score_head.py`: `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`.
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `tests/entities.py`: `2 of 2425 ENTITY CHECKS FAILED`. Both are `hb:positive_control` on its final try (`py-spy rc=0 names it: False`; one sample `TimeoutExpired ... after 0.5 seconds`). This is the same pair round 1 recorded on this branch and reproduced at its own pre-merge base `145bfe197`. It is this seat's py-spy sampling the heartbeat lane's spin. This diff touches no file that lane runs (`tests/nightly_ha.py`, the coordinator). It was not re-run at `e97f5749b`.
  - The `run_always` set: `tests/layout.py` rc=0; `tests/closure.py selftest` `ALL 117 closure shrink pins PASSED`; `tests/env_drift.py --claims-only e97f5749b441b282e43bd99dbcbb762e9d10a369` `claims hygiene: e97f5749b441b282e43bd99dbcbb762e9d10a369 ok`.
  - `tests/stress.py` is left to CI's required mutation check (`fixer.md` step 5).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` reads `CI PREDICT: no closures or fast red predicted against e97f5749b441`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` reads `0 refused`.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL`. No production line changed, and the score does not read `seam_cut_total` (`tools/audit/archscore/vector.py` stubs `seam_metrics`).

## Red checks

none: no CI has run on this head, and `ci_predict.py` predicts nothing red. The local `hb:positive_control` red under `## Figures` is a py-spy sampling red on this seat, in a lane this diff does not touch.

## Forward-carry

n/a: the roster's only group carrying `seam_cut_total` or O19 is this one. Every later stage derives the metric at its own merge base, so no figure needs carrying. A branch in flight that re-recorded `seam_cut_total` will conflict on `tests/structure_budgets.json` and re-records at its merge with main. That is a merge mechanic, not a finding.

## Friction

none
