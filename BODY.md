Class N-move-stale-path (#2312), the sibling seams PR #2289's stale-path arm left open, verified by two fix reviewers of that PR and filed so #2289 could close the class's first seams with these as named destinations. Three findings, one arm:

- **F1** — the cited-program arm's shape reader resolved a path literal only one hop from the open. The #2289 round-1 review planted 8 of 13 shapes escaping it (an alias, a join, a pathlib `/` read with `.read_text()`, an f-string prefix, a dict subscript, a tuple unpack, an annotated assignment); this pull request's round-1 review (#2344) named two more that are plainly inside the same rule -- a `for` target and `.open()` on a `/`-join receiver -- and the binding family beside them.
- **F2** — the arm's sources (a carry's JSON, and the policy corpus `tools/policy/policy_lint.mjs`'s own `policyFiles()` names) were INERT and read from the index, so a pull request that only added a broken citation was SCOPED to zero scripts and `main`'s forced full run caught it one merge later.
- **F4** — `dev/programme/carries/carry-201.json`'s `from`, `control` and `brief` prose still spelled 30 moved paths.

What changes:
- `tests/entities.py`: `_sp_literals` now follows a literal through every binding the module makes (`_sp_bindings`), a join, an f-string, a dict or list subscript, a held tuple, and -- the shape this round added -- a receiver (`.open()`, `.read_text()`), resolved in the scope that reads the name (`_sp_scope_map`), so a `line` bound in one function is not read as another's. The arm's own check plants 23 open shapes and 3 held controls, both reviews' lists as the control, so the class is pinned in the tree and not only in the out-of-tree drivers.
- `tests/closure.py`: `_is_citation_source` takes the arm's sources off `INERT`, and `tests/entities.py` reads them from the worktree, so an edit to a carry or a policy file selects this script -- the late-gate shape #518 and #533 closed the same way.
- `dev/programme/carries/carry-201.json`: every moved spelling re-pointed onto the path its file now lives at.

Rejected alternatives:
- Reading the sources from the index and pinning the arm some other way. It is the contradiction -- a file the gate reads and declares unread -- that F2 names, and #357 refuses the pair.
- Keying the shape reader on every literal. The arm would over-fire on `codeowners_gap.py`'s classifier inputs; the review's own ablation of that shape fires exactly those four.
- Binding a `for x in <expression>` target. It takes whatever the expression yields, and binding it reads an unrelated loop's classifier inputs as this one's opens -- `codeowners_gap.py` again, whose `line`, `want` and `ok` are the four that fire. Only a `for` over a literal collection is followed.
- Not scoping the bindings. A flat name -> value map is what produced those same four false faults: mutation M6 below shows the check failing when the resolution goes back to one map.
- Re-pointing carry-201's three residual citations of `tools/audit/round4/`. The two files they name still live there (the R9-RO-8 pin), so the re-point would name a non-existent file.

Closes #2312.

## Head

`32d426082e49495b9b5bcbd6d85eb2dda4d4458a`. Its merge base with `origin/main` is `92accb2cff702c910d33ee1a276d38f5b482061c`. Every figure below was taken at this head.

## Mutation proof

Each mutation deletes one line of the fix and was restored with `cp` from a preserved copy. The arm block alone is driven by the fix review's own round-1 `arm.py` with `ARM_EXTRA` unset.
- M1, `_sp_reach` stops following a bound name (the scope-walking key resolution replaced by `key = None`): FAIL the round-1-shapes check *and* the pre-existing cited-program check.
- M2, `_SP_READS` dropped from the open-site test: FAIL the round-1-shapes check.
- M3, the f-string leading-slash strip (`v = n.value[1:] if id(n) in fstr and n.value.startswith("/") else n.value` -> `v = n.value`) removed: FAIL the round-1-shapes check.
- M4, the receiver branch removed (a method call's path is then only read from its arguments): FAIL the round-1-shapes check (the `.open()` and name-via-`/` pairs).
- M5, the `for`-target binding removed: FAIL the round-1-shapes check.
- M6, the scope chain replaced by one flat map: FAIL the pre-existing cited-program check -- four `codeowners_gap.py` classifier inputs read as opens, the leak the scoping closes.
- M4a, `_is_citation_source` taken back off the `is_inert` override: FAIL the sources-select check (49 sources back on `INERT`).
- M4b, `tests/closures.json` reverted to the merge base (the 49 sources not recorded): FAIL the sources-select check (a source then selects the whole suite, not this script).
- M0, the unmodified tree (the null run): all four arm checks PASS.

## Null control

- The arm's held-literal controls are plants in the shapes check: a tuple, a set and a comparison holding the retired path must read as NO open, and the five shapes the arm already caught (`one-hop name`, `pathlib / in open`, `f-string bare`, `str concat`, `Path(lit).read_text()`) must still read as opens. All hold at this head, and the caught five fail under M1-M5.
- The scope resolution's own control is M6: with one flat map the reader fires four false opens on `codeowners_gap.py`; with the scopes it fires none.
- The arm's floors are unchanged: it still requires >= 20 policy files and >= 1 carry, and still finds 5 cited programs, all of which run (`_SP_STALE_RUN=[]`).
- The citation-source predicate's set is exactly the arm's read set: the 49 files `_is_citation_source` returns are byte-for-byte the union of `policyFiles()` (located) and `dev/programme/carries/carry-*.json` -- measured, no file in one and not the other.
- `tests/entities.py` still passes its own `orphan_files` and `inert_closure_violations` checks, which is what refuses a source the predicate names but the arm does not read.

## Figures

- `python3 tests/closure.py select --files dev/programme/carries/carry-201.json` -> `MODE: SCOPED -- 1 script(s) run`, `scope.run` naming `tests/entities.py`; the same command at the merge base reads `MODE: SCOPED -- 0 script(s) run`. (F2's repro; the late-gate shape.)
- The fix review's `arm.py` driven with #2289's round-1 `plants.py` as `ARM_EXTRA`: 8 ESCAPES / 5 REFUSED at the merge base, 0 ESCAPES / 13 REFUSED at this head. (F1's own harness, both ends.)
- The class enumerator is the arm's own check: 23 planted open shapes and 3 held controls, all reading as the rule says at this head, every one of the 23 failing under M1-M5 (the reader is what reads them). A separate 27-shape probe of mine reads 22 escapes at the merge base and 0 at this head; the two shapes #2344 named -- `for _P in (<retired>,): open(_P)` and `(Path('.') / <retired>).open()` / `_P.open()` -- are in both lists.
- The fix review's positive control, `_P = Path('.') / 'dev/nope_xyz/file.py'; _X = _P.open()`: read as an open at this head.
- A probe applying the review's moved-spelling rule to carry-201's `from`/`control`/`brief`: 30 at the merge base, 0 at this head. (F4's count.)
- `python3 tests/layout.py --report --verbose`, reference arm, for `carries/carry-201.json`: 30 lines (15 distinct line numbers) at the merge base, 3 at this head. The 3 are the pinned-file directory `tools/audit/round4/`, whose two files still live there (see Rejected alternatives).
- Scoped gate: `MODE: FULL` -- `tests/closure.py` changes the gate itself, so every closure is suspect.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py selftest` -> `ALL 115 closure shrink pins PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -> `ALL 2333 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -> `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/layout.py --guard` -> `0 refusal(s)`; `closure.orphan_files()` -> `0`.

## Red checks

none: no check-run has gone red on any commit of this branch. The code head `04fcb74f2` carries 45 check-runs (24 success, 12 skipped, 1 neutral, 8 cancelled -- a superseded generation, no failure), and this head has none yet.

## Forward-carry

The residual at this head is the 3 reference-arm lines of `dev/programme/carries/carry-201.json` citing `tools/audit/round4/`, where the R9-RO-8 pin keeps two files. They are recorded in that carry's fifth entry (its `brief`, "Constraint on preparing the NEXT round's baseline", and its `control`), which names the two files and their pin. The stage that ends the pin, R9-RO-9, is the subject of `dev/programme/carries/carry-1922.json`, which carries the move of `tools/audit/round4/D11/governance_cost.py`. No other finding changes how a later stage must work.

## Friction

- fixer.md: unclear: step 3 requires re-executing "the finding's harness" before and after, but a fix review's harness lives only in its verdict evidence (round 1's arm.py and plants.py here), while step 18 says a harness a later seat must rerun lands in dev/audit/harnesses/ -- no rule says whether a reviewer's one-shot driver belongs in the tree.
