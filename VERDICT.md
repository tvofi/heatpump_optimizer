Fix review: blocked 8c758b72c6ff16dd510a78b80110f744aac43ce8 defect: INERT READS downgraded to a warning on a diff CI's closures job never records (skip arm); mutation: direct-push rule survivors M5, M6
bus-nonce: 1bd79e4f27c18d9bd6ca8141709e5989

Round 2, delta review of #2061 from cf84e0a4 to 8c758b72 (4cdba2ac1, c94842ed9, d6d1196db, fc8c7aae8, 2aacc72fb + main merges). Live head re-read at posting: unchanged. roles/ diff vs main: empty.

## 1. INERT READS as a warning: it hides a real under-scope (blocking)
The premise in c94842ed9 -- "closures-autofix merges it after the push" -- holds only when CI's `closures` job takes its full arm. It does not hold for a diff whose changed files are all INERT and absent from every closure, which is exactly the diff that adds a harness file and nothing else:
- RESULT plant (plant_inert.sh, mine): a branch adding only `dev/audit/harnesses/zz_planted.py`. At head: `PREDICT closures INERT READS tests/harness_headers.py: ... (a new file beside 14 it lists)`, `predict rc=0`. At 4cdba2ac1 (pre-downgrade ci_predict): same line, `rc=1`.
- RESULT `tests/closure.py affected` on that diff: `case=skip`. The tests.yml `closures` job then runs the DOCS_ONLY_FAST arm: no recording, no `closure.py check`, so no INERT READS red on the PR, and `closures-autofix` (PR-only, runs on a `closures` failure) never fires. Required `closures` is green.
- `tests/harness_headers.py:311-318` rglobs `dev/audit/harnesses`; its committed inert_reads lists 21 files there. After merge, main's push runs the full arm, which records the new read and goes red with INERT READS UNDER-APPROXIMATED. Nothing repairs it on main, because closures-autofix is `pull_request`-only. I did not run main's Linux recording (heavy/strace); the chain above is each link read or measured.
- Before this change prepr 6d refused this diff locally, so the prediction was its only pre-merge detector. The PR's own self-test fixture `pinert` is this harness-only diff, so the new line `and an INERT READS red warns, never refuses` pins the hole as intended behaviour.
- Red-first confirmed: prepr --self-test at 4cdba2ac1 `219 passed, 1 failed` (that line), at head `220 passed, 0 failed`. Null control `an UNDER-SCOPED red still refuses` passes at head.
- Suggested repair, the fixer's call: warn only when the diff takes the full closures arm (`closure.py affected` case != skip); refuse, or require the diff to carry a non-inert file, on `skip`. Add the harness-only plant as a refusal case and the full-arm plant as the warning case.
- The motivating defect (seats hand-editing tests/closures.json for #2025, #2054, #2056) is real. Those diffs carried code, so the full arm ran. The downgrade is sound for them and unsound for the skip arm.

## 2. Direct-push disposition rule: sound in shape, under-pinned (blocking with 1)
- RESULT v6.7.17 window (`--check --since 1913f0dd`, base vs head delivery_status.py): base 9 unread; head 4 `exempt ... record-only` (0a60e06, d579544, 6b1ccb6, 62f604e, each a rows-only first-parent diff) and 5 still unread (618d014, f6ac991, 077f53a, 130c780, 8107181: code merges, correctly UNCHECKED; direct-pushes.md has no lines yet). Verdict UNCHECKED at both ends, which is correct.
- RESULT attack cases at head (ds_disp.py, mine): rows-only record-only; code needs an allow line; rows+script, files unknown, files empty, a commit touching only direct-pushes.md, a `.md.bak` lookalike, a nested path, an allow line for another sha, a 6-hex allow key: all UNCHECKED. Pre-move row path: record-only, via locate. The rule behaves correctly.
- Mutation, running the PR's own entities.py block verbatim against mutated copies (ent_block.py):
  - base FAIL (TypeError, no allow parameter), so red first.
  - Killed: M1 (`all` changed to `any`), M2 (the blind list unfiltered), M4 (allow lines ignored).
  - **Survivors:** M5 `sha.startswith(k)` changed to `True`, which lets one allow line exempt every unnumbered merge (my harness: allow-other-sha goes UNCHECKED to EMPTY). M6 ROW_FILE loosened to any path under dev/programme/delivery/, which makes a push that edits only direct-pushes.md (the allow list itself) or a `1998.md.bak` record-only.
  - Also surviving: M3, `files and` changed to `files is not None`, which makes an empty diff record-only. That is harmless, so I note it only.
- M5 is the guarantee the commit message states: "exempt only through a line ... naming its sha". It is unpinned. Two cases close both survivors: an allow line for another sha stays UNCHECKED, and a commit touching only direct-pushes.md stays UNCHECKED.

## 3. Rest of the delta
- 2aacc72fb: the delivery row for #2061 is present.
- Main merges: carried, CI green.
- Check-runs at 8c758b72 (40, settled): everything green except `nightly-status`, which is last night's nightly and reads no file in this diff, so it is not this PR's.
- Round-1 RESULTs not re-taken. My delta review read the merge commits by their paths only: a206b5056, cdc063d5f and 8c758b72c bring in main (v6.7.17 stamp and others) and touch no file of this PR's own code.
