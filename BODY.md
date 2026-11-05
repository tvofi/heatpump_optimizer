R10-FLY-ARCHSCORE-STMT-PACKING, repair round 3. `coord_footprint` (counter C25) reads a packed statement as the plain statements it spells. This round closes the conditional chain nested in the body arm (round 2 block, attempt 54), removes the starred-target over-count, answers `## Red checks`, and disposes the remaining over-count and unclosed shapes in `tools/audit/archscore/ABOUT.md`.

What changed:
- `footprint._chain` counts the branches of a conditional-expression TREE: every `IfExp` reachable through `body` as well as `orelse` (`(a if q else b) if p else c` is three branches, as its nested if/else spells). `_extras` skips every `IfExp` nested directly under another, so the tree is charged once at its root.
- `footprint._bound`: a tuple target holding a starred element against a display value reads the names it binds. `a, *b = e1, e2, e3` reads 2, as `a = e1; b = [e2, e3]` does (it read 3).
- Plant 54 (`planted/redteam/54_footprint_ifexp_body_chain.py`), the reviewer's `x = ((A) if (p) else (B)) if (p) or (q) else (C)` respelling of each if/elif/else of the coordinator: recorded GAME, NULL, admissible.
- Plant 55 (`planted/redteam/55_footprint_boolop_control.py`), `if p: x = A / else: x = B` respelled `x = (p) and (A) or (B)`: it reads IMPROVES (admissible), so it is recorded KNOWN-OPEN through `planted/cases.py` `KNOWN_OPEN`, not closed. The disposition is in ABOUT.md (design choice, below).
- `tests/arch_score.py`: four new rows of the packed/plain table (the body-arm tree, a tree in both arms, `a, *b` and `*a, b`).
- ABOUT.md dispositions, each with the reason: `for` over a literal of tuples and its `async for` twin (over-count, safe direction; the loop body is written once); `p and A or B` (attempt 55, KNOWN-OPEN); a comprehension used as a loop over a literal (open by design, not planted: a comprehension is also a mapping).

Design choice, said where it is made: counting a `BoolOp` as control flow was not built. `a or b` and `a and b` are idioms and no structural test separates control flow from them, so a counter would charge ordinary code; the respelling is the same bounded 3-to-1 as the lone `a if p else y` already disposed in ABOUT.md. The alternative (count `A and B or C` as a two-branch tree) was rejected for that reason; a class fix flips attempt 55 and `tests/arch_score.py` then refuses until it is re-recorded.

Closes the round 2 block of #3218. No issue is closed by this repair.

## Head

c161f41eaf5021a507292d3d141cf80d306e6edb (merges origin/main 8364e6246 into the round 2 head c8204eb83; main moved after the PR head, so `tools/pr/prepr.sh` was rerun on this head). The heavy lanes of c8204eb83 were CANCELLED by ci_priority.py's pause, not red: the next head needs a full CI code run, which this push provides.

## Mutation proof

Failing test first, importing the production symbol (`footprint.logic_stmts`): with the production edits to `footprint.py` stashed and the four new rows in `tests/arch_score.py`, the packed spelling read 1 against 5 for `a = (f(x + 1) if q else g(y + 1)) if p else h(z + 1)` and 3 against 2 for `a, *b = f(x + 1), g(y + 1), h(z + 1)`; with the edits restored they read 5/5 and 2/2. Command: `PYTHONPATH=tests/hastub python3 -c` over `footprint.logic_stmts(ast.parse(src))` for each pair, run at both ends.

Attempt 54 before the repair: the reviewer measured IMPROVES dS +0.0022 on the coordinator at c8204eb83 (probe/rev-3218-927b3349, ev/rv_plants_calibrate.txt); after, `calibrate.py --only rt_54_footprint_ifexp_body_chain` reads NULL, admissible, and `tests/arch_score.py` classifies it as recorded. I did not re-run the pre-repair plant myself; the pre-repair figure is the reviewer's, using the plant script this PR commits at the same path with a new docstring.

## Null control

`rt_00_null_rename` reads NULL in the same `tests/arch_score.py` run. The mutant for the packing attempts is `ARCHSCORE_ABLATE=C25`, unchanged this round; I did not re-run rt_48 to rt_53 under it (round 2 and the round 2 reviewer measured them IMPROVES). The control for the star and body-arm rows is the table's own plain spelling: each packed row must equal its plain twin, and the unfixed tree above reads 1 against 5 and 3 against 2.

#3185 (the finder's case, d7582ed4 base, cc67aa45 head) at this head, packed against plain, same instrument and the same pair of trees, the plain spelling being cc67aa45 with the generator unpack replaced by four `self._x = self._x if n[i] is None else n[i]` (rebuilt this round, local commit, not pushed):

| spelling | no ablation | `ARCHSCORE_ABLATE=C25` |
|---|---|---|
| packed cc67aa45 | dS +0.0069, footprint 2513 -> 2501 | dS +0.0042, 2381 -> 2374 |
| plain | dS +0.0075, footprint 2513 -> 2500 | dS +0.0030, 2381 -> 2376 |

At the head packed and plain read within one statement. At the C25-off end packed beats plain by two statements, which is the defect this PR fixes.

## Figures

- Packed and plain on #3185: `python3 tools/audit/archscore/score.py --diff d7582ed4 <spelling>`, `ARCHSCORE_ABLATE=C25` prefixed for the right column. Values in the table above.
- Real diff: `python3 tools/audit/archscore/score.py --diff origin/main HEAD` at head fec573f3c (before the origin/main merge): "Architecture score: dS +0.0000 NULL". The diff is under `tools/audit/archscore/` and `tests/`, outside the scored package.
- Stored corpus: `calibrate.py --measure-corpus --only-metric footprint` finished rc=0 and left `calibration/corpus_vectors.json` byte-identical to the round 2 head, so no corpus verdict moved.
- `PYTHONPATH=tests/hastub python3 tests/arch_score.py`: "ALL 279 ARCHITECTURE SCORE CHECKS PASSED" at the pre-merge head; the rerun on this head is in the Gate line below.
- Seam enumeration for the class "a conditional or control-flow shape that packs several statements": the rule is the C25 row of ABOUT.md plus `tests/arch_score.py`'s table, driven by the sibling script `sib2.py`/`54_rv_ifexp_body_chain.py` of the reviewer (instruments of probe/rev-3218-927b3349). Returned seams and dispositions: body-arm tree, closed (attempt 54); starred target, closed (table rows); `for` over a literal of tuples and `async for`, over-count disposed in ABOUT.md; BoolOp control flow, KNOWN-OPEN (attempt 55); comprehension over a literal, disposed in ABOUT.md, not planted; walrus in a call, over-count of one, safe direction, disposed in round 2. No instrument enumerates the class syntactically; the table and the planted attempts are what was done instead.
- Toolchain: `python3 -c 'import numpy,scipy'` prints numpy 2.5.4 and scipy 1.18.1, equal to `tests/requirements-ci.txt`; `cloud-setup.sh --check` read OK. CI remains the authority for goldens, none of which this diff touches.

Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 3 script(s) run, 30 scoped out` (arch_score, arch_score_head, entities, before the origin/main merge). `arch_score_head.py` (18 checks), `entities.py` (2617 checks) and `structure.py` ("STRUCTURE RATCHET PASSED") ran green; `tests/structure.py` and every `*_budgets.json` are untouched and no budget is raised. Claim files are byte-identical to origin/main (three-dot diff lists neither). VERSION, the manifest version and the RELEASE_NOTES heading are untouched.

## Architecture score

Real diff: dS +0.0000 NULL (above). The change adds no scored statement; `tools/audit/archscore/score.py --diff` is the instrument.

## Red checks

Named by exact check-run name, from the red-history of the 9 commits of c8204eb83 (the reviewer's ev/checks_nongreen.tsv):

- `tests / closures`: this branch's own red. Cause: plants 48 to 53 and the `arch_score.py` closure were new files and a stale closure entry. closures-autofix repaired it with a bot commit. Cheaper detector: `tools/pr/ci_predict.py` (UNCLASSIFIED / UNDER-SCOPED arms), which exists and ran here in under 110 s on this branch and predicted the same arm for plants 54 and 55 and the interim PR-BODY.md before the push; repaired with `tests/derive_closures.sh --single tests/arch_score.py`. Standing cost: one `ci_predict.py` run per handoff, which finished inside a 110 s limit here. The second trigger of defect-root-cause.md applies (the same failure was reachable earlier and cheaper); the detector exists and is named in `fixer.md` step 5, so no new countermeasure is built, and the process state is (b): it existed and was not run before the c8204eb83 push.
- `pr-contract / pr-contract`: red because this section did not name `tests / closures`. Answered here.
- `governance / delivery-status` and `tests / nightly-status`: red on main's ancestry, not this branch's. They grade `main`; the base is 8364e6246 and the three-dot diff touches neither script, `ci.yml`, `tests.yml`, `nightly.yml`, `governance.yml`, the plan nor `HANDOVER.md`, only this PR's own row `dev/programme/delivery/3218.md`. No answer owed (defect-root-cause.md, Enforcement).
- The CANCELLED lanes of c8204eb83 (`tests / fast (3.14)`, `tests / closures`, `tests / arch-instrument`, `tests / coverage`, `governance / env-matrix`, `governance / instrument-self-tests`, `codeql / Analyze (python)`) were ci_priority.py's pause, not a red. The next head needs a full CI code run.

## Unpinned sites

`tools/` sites only; the mutation-autofix lane mutates `custom_components/` only. `footprint._chain`/`_bound` are covered by an in-tree mutant: `tests/arch_score.py`'s packed/plain table fails when `_chain` follows only `orelse` (the unfixed run above is that mutant).

## Forward-carry

none

## Friction

none
