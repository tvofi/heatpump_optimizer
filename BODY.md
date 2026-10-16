Class N-move-stale-path (#2312), the sibling seams PR #2289's stale-path arm left open, verified by two fix reviewers of that PR and filed so #2289 could close the class's first seams with these as named destinations. Three findings, one arm:

- **F1** — the cited-program arm's shape reader resolved a path literal only one hop from the open. Eight of thirteen open shapes the round-1 review planted escaped it: an alias, a join, a pathlib `/` read with `.read_text()`, an f-string prefix, a dict subscript, a tuple unpack and an annotated assignment.
- **F2** — the arm's sources (a carry's JSON, and the policy corpus `tools/policy/policy_lint.mjs`'s own `policyFiles()` names) were INERT and read from the index, so a pull request that only added a broken citation was SCOPED to zero scripts and `main`'s forced full run caught it one merge later.
- **F4** — `dev/programme/carries/carry-201.json`'s `from`, `control` and `brief` prose still spelled 30 moved paths.

What changes:
- `tests/entities.py`: `_sp_literals` now follows a literal through every binding, join, dict subscript, f-string and read site (`_sp_bindings` / `_sp_reach`), and the arm's check plants each of the eight shapes the round-1 review named, with the five it already caught kept as controls.
- `tests/closure.py`: `_is_citation_source` takes the arm's sources off `INERT`, and `tests/entities.py` reads them from the worktree, so an edit to a carry or a policy file selects this script — the late-gate shape #518 and #533 closed the same way.
- `dev/programme/carries/carry-201.json`: every moved spelling re-pointed onto the path its file now lives at.

Rejected alternatives:
- Reading the sources from the index and pinning the arm some other way. It is the contradiction — a file the gate reads and declares unread — that F2 names, and #357 refuses the pair.
- Keying the shape reader on every literal (the arm would over-fire on `codeowners_gap.py`'s classifier inputs).
- Re-pointing carry-201's three residual citations of `tools/audit/round4/`. The two files they name still live there (the R9-RO-8 pin), so the re-point would name a non-existent file.

Closes #2312.

## Head

`d48519cd02aba76c58eabbb8161f5a5886e65ca5`. Its merge base with `origin/main` is `92accb2cff702c910d33ee1a276d38f5b482061c`. Every figure below was taken at this head.

## Mutation proof

Each mutation deletes one line of the fix and was restored with `cp` from a preserved copy. The arm block alone is driven by the fix review's own `arm.py` (`dev/audit/...` round-1 evidence) with `ARM_EXTRA` unset.
- M1, `_sp_reach` no longer follows a bound name (`stack.extend(binds.get(n.id, ()))` deleted): FAIL the round-1-shapes check *and* the pre-existing cited-program check.
- M2, the `_SP_READS` branch deleted: FAIL the round-1-shapes check.
- M3, the leading-slash strip (`v = n.value[1:] if n.value.startswith("/") else n.value` -> `v = n.value`) removed: FAIL the round-1-shapes check.
- M4a, `_is_citation_source` taken back off the `is_inert` override: FAIL the sources-select check (49 files back on `INERT`).
- M4b, `tests/closures.json` reverted to the merge base (the 49 sources not recorded): FAIL the sources-select check (a source then selects the whole suite, not this script).
- M0, the unmodified tree (the null run): all four arm checks PASS.

## Null control

- The arm's held-literal control is a plant in the shapes check: `_X = (<retired>,)` must read as NO open, and the five shapes the arm already caught (`one-hop name`, `pathlib / in open`, `f-string bare`, `str concat`, `Path(lit).read_text()`) must still read as opens. All six hold at this head, and every one of them fails under M1/M2/M3.
- The arm's floors are unchanged: it still requires >= 20 policy files and >= 1 carry, and still finds 5 cited programs, all of which run (`_SP_STALE_RUN=[]`).
- The citation-source predicate's set is exactly the arm's read set: the 49 files `_is_citation_source` returns are byte-for-byte the union of `policyFiles()` (located) and `dev/programme/carries/carry-*.json` — measured, no file in one and not the other.
- `tests/entities.py` still passes its own `orphan_files` and `inert_closure_violations` checks, which is what refuses a source the predicate names but the arm does not read.

## Figures

- `python3 tests/closure.py select --files dev/programme/carries/carry-201.json` -> `MODE: SCOPED -- 1 script(s) run`, `scope.run` naming `tests/entities.py`; the same command at the merge base reads `MODE: SCOPED -- 0 script(s) run`. (F2's repro; the late-gate shape.)
- The fix review's `arm.py` driven with its own round-1 `plants.py` as `ARM_EXTRA`: 8 ESCAPES / 5 REFUSED at the merge base, 0 ESCAPES / 13 REFUSED at this head. (F1's own harness, both ends.)
- A probe applying the review's moved-spelling rule to carry-201's `from`/`control`/`brief`: 30 at the merge base, 0 at this head. (F4's count.)
- `python3 tests/layout.py --report --verbose`, reference arm, for `carries/carry-201.json`: 16 lines at the merge base, 3 at this head. The 3 are the pinned-file directory `tools/audit/round4/`, whose two files still live there (see Rejected alternatives).
- Scoped gate: `MODE: FULL` — `tests/closure.py` changes the gate itself, so every closure is suspect.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py selftest` -> `ALL 115 closure shrink pins PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -> `ALL 2333 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -> `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/layout.py --guard` -> `0 refusal(s)`; `closure.orphan_files()` -> `0`.

## Red checks

none. Every check-run at the reviewed head is green; the diff never turned one red.

## Forward-carry

The residual at this head is the 3 reference-arm lines of `dev/programme/carries/carry-201.json` citing `tools/audit/round4/`, where the R9-RO-8 pin keeps two files. They are already recorded in this same carry's fifth entry, which names them and the R9-RO-9 that ends the pin, so no new destination is owed. No other finding changes how a later stage must work.

## Friction

unclear: `dev/governance/roles/fixer.md`: step 3 asks for the finding's harness "before and after" but a reviewer's harness lives only in their verdict evidence (round-1 `arm.py`/`plants.py` here), not in `dev/audit/harnesses/`; step 18 says a harness a later seat must rerun lands in the tree, which is not what the fix review's own driver does.
