Fix review: blocked 54bfc9934041d594510309310ec427896e6d715e root-cause-unanswered: closures went red, unanswered (INERT READS UNDER-APPROXIMATED: tests/doc_claims.py now reads docs/site/docs.css, which its inert_reads entry does not list; pr-contract, a required check, refuses on it)

bus-nonce: 6c4932190496f4206e243e4d3e7b98f0

Round 2. PR #1864 (R9-WEB-3), head 54bfc9934041d594510309310ec427896e6d715e. I re-read the live head after CI finished, and it had not moved. The authored code head is f415763d, carrying the fix commit dbf4aa30. The main merge brings in v6.7.14 at 03ba7f70. Evidence for this round is in ev2/; HEAD.txt names the head. All three round-1 items are closed. The round-1 stylesheet fix opened one new red check.

## Owed (one item)

**`closures` is red, and the round-1 fix caused it.** The CI closures job (job 111042803895, `SCOPE_CASE: full`) printed:

    INERT READS UNDER-APPROXIMATED: ... tests/doc_claims.py: docs/site/docs.css

`subpage_findings` now opens `docs/site/docs.css`, which is the round-1 stylesheet scan. That file is INERT, and `tests/closures.json` has no `inert_reads` entry for `tests/doc_claims.py`. The entry's keys are `tests/harness_headers.py` and `tests/entities.py` only.

The autofix does not repair it. `closures-autofix` printed `AUTOFIX: skip-not-under-scoped` and `nothing owed to a human`. That message is false for this red: the repair is owed to the fixer.

- Fix: add `docs/site/docs.css` under `inert_reads["tests/doc_claims.py"]`. The Linux recording in the `closure-recordings` artifact 11254298147 is the source; do not take a Darwin `--single` recording whole, because round 1 showed it is lossy for entities.py.
- Then name `closures` in `## Red checks` with its cheaper detector. pr-contract (job 111050506824) refuses with `check closures is red and ## Red checks does not name it`.

## Round-1 owed list: all closed

1. **briefs.** RESULT `node .claude/workflows/brief_lint.mjs` at the head: rc 0. CI briefs: success. The five citations in carry-1645.json moved by 8 lines. `## Red checks` answers briefs with its cause and its cheaper detector.
2. **Stylesheet scan.** My round-1 controls (`reviewer_controls.sh`) at this head:
   - RESULT C1, a Google Fonts `@import url(...)` in docs.css: `3 of 153 checks FAILED`
   - RESULT C2, a third-party `@font-face src`: `3 of 153 checks FAILED`
   - RESULT unplanted: `ALL 153 checks PASSED`
   - RESULT `@IMPORT url(...)`: red, caught through the `url(` alternative.
   - The in-arm controls cover both plants, a missing linked stylesheet, a third-party srcset candidate and the clean baseline. WEB-1's inline-CSS regex hole for `@import url(` is fixed too.
3. **Duplicate page name.** I turned build line 50 (`errors.push('two documents would ...')`) into `void 0` in the real tools/site/build_docs.mjs. RESULT: doc_claims prints `FAIL two anchor-free documents with one page name are red, naming the collision [rc 0, []]`. The committed arm now kills it, which is better than a scratch-only control. mutate_build.py: RESULT 9 KILLED, 1 SURVIVED (line 227, zero pages, equivalent as ruled in round 1).

## Arm mutation and the three crashes

`mutate_arm_rev2.py` is my harness, re-keyed to merge base 03ba7f70.
- RESULT baseline: `in_tree_failures=0 anchor:RED untracked-link:RED`
- RESULT: 33 mutable lines, 29 KILLED, 1 SURVIVED, 3 CRASH.
- The survivor is L2350 `if kind == "third-party":` in the control loop. I accept it, as in round 1.

**My ruling on the crashes: all three are killed.** My harness separates crashes so that a broken harness cannot count as kills; that is what happened to the fixer's original script in round 1. It does not make a crash a survivor. I ran each crash mutant through `tests/doc_claims.py` itself:
- L2072 `if not css.is_file():` turned to `if False:`: RESULT rc 1, `FileNotFoundError ... docs/site/docs.css`. The missing-stylesheet control reaches the mutated branch, the read raises, and the run goes red.
- L2384 `if readme:` and L2389 `if git:` are test-fixture code in the corpus builder. RESULT rc 1 for both (`FileNotFoundError ... README.md` and `CalledProcessError git add`).
- A doc_claims run that crashes is a red CI run. The tally is 32 of 33 killed and 1 accepted survivor.

## Checked at this head

- RESULT local runs at this head:
  - `tests/doc_claims.py`: `ALL 153 checks PASSED`
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)`
  - `tests/layout.py`: `layout self-test: ok`
  - `git merge-tree --write-tree origin/main HEAD`: clean
- Three-dot from the merge base: no VERSION, custom_components, golden or release-notes change.
- RESULT waitci: `DONE total=35`, NOTGREEN `closures`, `nightly-status` and `pr-contract`.
  - nightly-status is main's red. The diff reaches nothing it reads, and the body says so.
  - `mutation` is green. This diff changes no production line, so no mutant was drawn.

## Not blocking

- `URL(https://...)` (uppercase) and `image-set("https://..." 1x)` in docs.css pass the scan. RESULT: `ALL 153 checks PASSED` for each. Both need deliberate spelling; an accidental Google Fonts paste is caught. A `re.I` on the url alternative would close the first.
