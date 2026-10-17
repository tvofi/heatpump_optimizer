Class N-move-stale-path (#2312), the sibling seams PR #2289's stale-path arm left open, verified by two fix reviewers of that PR and filed so #2289 could close the class's first seams with these as named destinations. Three findings, one arm:

- **F1** — the cited-program arm's shape reader resolved a path literal only one hop from the open. The #2289 round-1 review planted 8 of 13 shapes escaping it (an alias, a join, a pathlib `/` read with `.read_text()`, an f-string prefix, a dict subscript, a tuple unpack, an annotated assignment); this pull request's round-1 review (#2344) named two more that are plainly inside the same rule -- a `for` target and `.open()` on a `/`-join receiver -- and the binding family beside them. Its round-2 review named the two remaining name-resolution escapes: a binding routed through a `global`/`nonlocal` declaration (closed this round), and an attribute bound in one scope read in another (dispositioned this round, below).
- **F2** — the arm's sources (a carry's JSON, and the policy corpus `tools/policy/policy_lint.mjs`'s own `policyFiles()` names) were INERT and read from the index, so a pull request that only added a broken citation was SCOPED to zero scripts and `main`'s forced full run caught it one merge later.
- **F4** — `dev/programme/carries/carry-201.json`'s `from`, `control` and `brief` prose still spelled 30 moved paths.

What changes:
- `tests/entities.py`: `_sp_literals` follows a literal through the bindings its resolver tracks -- a name bound to a value in the scope that reads it, re-routed through the scope a `global`/`nonlocal` declaration names (a `global _G` assignment inside a function is a module binding, so a module-level `open(_G)` reaches it), plus a join, an f-string, a dict or list subscript, a held tuple, and a receiver (`.open()`, `.read_text()`). The arm's own check plants 25 open shapes and 3 held controls, both reviews' lists as the control, so the class is pinned in the tree and not only in the out-of-tree drivers.
- `tests/entities.py`, the attribute shape: an attribute bound to a path literal in one scope and opened in another (`self._p` set in `__init__` and opened in a sibling method, `C.P` set in a class body and opened as `C.P`) is the one shape the name-only resolver does NOT follow -- `_sp_reach` keys a read by the attribute name and walks up only enclosing scopes, so a sibling-scope binding is invisible, and following it precisely needs object identity (which object does `self` name?) that the flat name map M6 removed over-fires on. **Disposition: already-guarded** -- the new census `_sp_attr_bound` asserts no cited program binds a path literal to an attribute or a class-body name at all, refuses the day one gains a writer (its planted `self._p` and `C.P` variants are the null control), and returns 0 live sites today.
- `tests/closure.py`: `_is_citation_source` takes the arm's sources off `INERT`, and `tests/entities.py` reads them from the worktree, so an edit to a carry or a policy file selects this script -- the late-gate shape #518 and #533 closed the same way.
- `dev/programme/carries/carry-201.json`: every moved spelling re-pointed onto the path its file now lives at.

Rejected alternatives:
- Reading the sources from the index and pinning the arm some other way. It is the contradiction -- a file the gate reads and declares unread -- that F2 names, and #357 refuses the pair.
- Keying the shape reader on every literal. The arm would over-fire on `codeowners_gap.py`'s classifier inputs; the review's own ablation of that shape fires exactly those four.
- Binding a `for x in <expression>` target. It takes whatever the expression yields, and binding it reads an unrelated loop's classifier inputs as this one's opens -- `codeowners_gap.py` again, whose `line`, `want` and `ok` are the four that fire. Only a `for` over a literal collection is followed.
- Not scoping the bindings. A flat name -> value map is what produced those same four false faults: mutation M6 below shows the check failing when the resolution goes back to one map.
- Following the attribute-bound-in-one-scope-opened-in-another shape with a flat attribute map. Pooling every `obj.attr = <path>` into one class-wide scope makes two `self._p` sites on different objects read as one open (the M6 leak, one level up); resolving it precisely means tracking which object each `self` is, which the arm does not do. The census refuses the day a cited program gains a writer, which is the guard the empty class warrants rather than a whole object model.
- Re-pointing carry-201's three residual citations of `tools/audit/round4/`. The two files they name still live there (the R9-RO-8 pin), so the re-point would name a non-existent file.

Closes #2312.

## Head

`1f310023781000f50b84f83846dfc0116c454eaf` re-routes a `global`/`nonlocal` binding to the scope its declaration names and adds the attribute census, on top of the round-2 head `a0743cfa2727cd010020e5aa39be31f443c37869`. Its merge base with `origin/main` is `e3f3b312fff572904f24d78a44a2c4492b1a8ddb`. Every figure below was taken at this head.

## Mutation proof

Each mutation deletes one production line of the fix and is restored from a preserved copy. The shape reader is driven directly (`_sp_literals` / `_sp_bindings` / `_sp_attr_bound`), and each mutation is named against the arm's check it fails in `tests/entities.py`.
- M7, the `global`/`nonlocal` re-routing removed (`eff` always returns its textual scope): FAIL the open-shapes check -- the two planted declarations "global binding" and "nonlocal binding" read as no open again, while the held-literal controls still hold. (Confirmed by the full `tests/entities.py` run going red at that check.)
- M8, the attribute census detection removed (`_sp_attr_bound` returns `[]`): FAIL the census check -- the two planted attribute variants stop firing, so `len(_sp_attr_planted) >= 2` reads false.
- M1-M6, M4a, M4b, M0 from the round-1/round-2 heads: their production lines are untouched by this round, and each still fails the check it names -- M1 (`_sp_reach` stops following a bound name) the open-shapes check and the cited-program check, M2 (`_SP_READS` dropped), M3 (the f-string leading-slash strip removed), M4 (the receiver branch removed), M5 (the `for`-target binding removed) the open-shapes check, M6 (the scope chain replaced by one flat map) the cited-program check with four `codeowners_gap.py` classifier inputs read as opens, M4a/M4b the sources-select check; M0 (the unmodified tree) passes all five arm checks.

## Null control

- The arm's held-literal controls are plants in the shapes check: a tuple, a set and a comparison holding the retired path must read as NO open, and the five shapes the arm already caught (`one-hop name`, `pathlib / in open`, `f-string bare`, `str concat`, `Path(lit).read_text()`) must still read as opens. All hold at this head.
- The scope resolution's own control is M6: with one flat map the reader fires four false opens on `codeowners_gap.py`; with the scopes it fires none. The `global`/`nonlocal` re-routing keeps the map scoped: a `global _G` assignment is a module binding, never a flat alias a sibling function's same-named local would read.
- The attribute census's own control is the planted pair: a `self._p` set in `__init__` and opened in another method, and a `class C: P = ...` opened as `C.P`, each read as a site by `_sp_attr_bound`, while a benign `self._x = "not-a-path"` reads as none.
- The arm's floors are unchanged: it still requires >= 20 policy files and >= 1 carry, and still finds 5 cited programs, all of which run (`_SP_STALE_RUN=[]`).
- The citation-source predicate's set is exactly the arm's read set: the 49 files `_is_citation_source` returns are the union of `policyFiles()` (located) and `dev/programme/carries/carry-*.json` -- measured at this head, no file in one and not the other.
- `tests/entities.py` still passes its own `orphan_files` and `inert_closure_violations` checks, which is what refuses a source the predicate names but the arm does not read.

## Figures

- The class enumerator is the arm's own check: 25 planted open shapes (the 23 from the two fix reviews plus "global binding" and "nonlocal binding") and 3 held controls, all reading as the rule says at this head; the 23 fail under M1-M5 and the 2 round-3 declarations under M7 (the reader is what reads them), and the 3 held stay held under the same mutations.
- The attribute enumerator is `_sp_attr_bound` run over the cited corpus: `[(p, sites) for p, sites in _sp_attr_sites if sites]` -> `[]` (0 live sites), and the planted `self._p` / `C.P` pair fires (the null control, `len(_sp_attr_planted) == 2`).
- The block's minimal `global` source (`_G = None; def load(): global _G; _G = <retired>; _X = open(_G)`) reads `<retired>` at this head and reads nothing at the round-2 head; the `nonlocal` twin reads `<retired>` here and nothing there.
- The fix review's `arm.py` driven with #2289's round-1 `plants.py` as `ARM_EXTRA`: 8 ESCAPES / 5 REFUSED at the merge base, 0 ESCAPES / 13 REFUSED at this head. (F1's own harness, both ends.)
- Scoped gate: `MODE: FULL` -- `tests/closure.py` changes the gate itself, so every closure is suspect.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py selftest` -> `ALL 115 closure shrink pins PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -> `ALL 2341 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -> `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/layout.py --guard` -> `0 refusal(s)`; `closure.orphan_files()` -> `0`.
- A probe applying the review's moved-spelling rule to carry-201's `from`/`control`/`brief`: 30 at the merge base, 0 at this head. (F4's count.)

## Red checks

none: no check-run has gone red on any commit of this branch. This head has not been pushed yet.

## Forward-carry

The attribute-bound-in-one-scope-opened-in-another shape (`self._p`, `C.P`) is the one open seam the name-only resolver leaves. Disposition: **already-guarded** -- the census in this diff asserts 0 live sites today and refuses the day a cited program gains a writer; a writer would then be a distinct finding, not a silently held path. No other finding changes how a later stage must work. The 3 reference-arm lines of `dev/programme/carries/carry-201.json` citing `tools/audit/round4/` remain as the round-2 forward-carry recorded.

## Friction

- fixer.md: unclear: step 3 requires re-executing "the finding's harness" before and after, but a fix review's harness lives only in its verdict evidence (round 1's arm.py and plants.py here), while step 18 says a harness a later seat must rerun lands in dev/audit/harnesses/ -- no rule says whether a reviewer's one-shot driver belongs in the tree.
