Fix review: blocked baadb84028a57add020bc166884d55d4d1259235 closures-under-approximated: tests/closures.json names no inert_reads entry for dev/audit/harnesses/eg_b7_seam_hubs.py; #2022 is not merged at this head

bus-nonce: d770ee69a6f7a083388ad9013e8a3659

Round 3 (round 2 returned `merge` at 46b9b4fd). Judged: only the resolution delta 46b9b4fd..baadb840. Live head at posting time re-read: baadb84028a57add020bc166884d55d4d1259235 (PR still DIRTY). origin/main is e0f0b6fb.

## Finding (blocking): claimed resolution 1 does not hold

- The head does not contain #2022. merge-base(origin/main, head) = 45142cc3 (#2012); origin/main e0f0b6fb is 3 commits ahead and contains 042b66fa, which adds `tools/audit/harnesses/eg_b7_seam_hubs.py` to `inert_reads["tests/harness_headers.py"]`.
- At the head, `grep -n eg_b7 tests/closures.json` returns nothing. Neither the old path nor the new path is listed. The file sits at `dev/audit/harnesses/eg_b7_seam_hubs.py`, and `tests/harness_headers.py` reads it (`_scope_paths()` adds `dev/audit/harnesses`).
- The PR body (line 37) says "No `closures.json` entry ... names it" and treats that as correct. It is the same gap that turned main's closures job red ("INERT READS UNDER-APPROXIMATED"), which #2022 fixed, now at the moved path.
- Simulated merge: `git merge-tree --write-tree origin/main HEAD` gives tree 5e0937fa. The local LEDGER-MERGE driver says it "resolved tests/closures.json" by merging the set. The merged table keeps the stale `tools/audit/harnesses/eg_b7_seam_hubs.py`, which does not exist in that tree, and still lacks the `dev/audit/` path. The merge does not repair it. GitHub cannot run that driver, which is why the PR is DIRTY and has no runs.
- Stand-in recording. I took a Darwin `derive_closures.sh --single tests/harness_headers.py --record-only` recording and set `inert_reads` to the read Linux strace recorded on main, then ran `closure.py check --in-dir <d> --partial`:
  - RESULT standin_eg_b7 (`dev/audit/harnesses/eg_b7_seam_hubs.py`) at head closures.json: rc=1, `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: dev/audit/harnesses/eg_b7_seam_hubs.py`
  - RESULT standin_eg_b7 against the merged tree's closures.json (5e0937fa): rc=1, same line
  - RESULT control (`dev/audit/harnesses/dual_path.py`, already listed) at head: rc=0
- The body's evidence for this item, `check --partial` printing "covers every file" (lines 39 and 71), is vacuous for this class. The Darwin recording has `how: audithook+sys.modules` and records **0** `inert_reads`. The committed list has 526 entries for this script, 14 of them under `dev/audit/harnesses/`. harness_headers.py reads the harnesses in child processes, which only Linux strace sees. My own unmodified Darwin recording also passes (rc=0) at head and at the merged tree. That pass is the instrument's blindness, not coverage.
- Required: merge origin/main (#2022), then replace `tools/audit/harnesses/eg_b7_seam_hubs.py` in `inert_reads["tests/harness_headers.py"]` with `dev/audit/harnesses/eg_b7_seam_hubs.py`, in sorted position. Correct the body lines 37, 39 and 71.
- Instrument note, which does not block this PR: `check`'s PHANTOM guard does not cover `inert_reads`. The merged table's dead old-path entry printed no PHANTOM. Main may already be affected after any move, so this goes to the instrument's stage, not to this PR.

## Claimed resolutions 2-5: verified

2. `dev/audit/rounds/round4/D6/claims.{json,md}`: main's 45142cc3 content, with `tools/audit/round4/D6` rewritten to the new path, is byte-equal (`cmp`) to the head's files. `PYTHONPATH=tests/hastub python dev/audit/rounds/round4/D6/claims.py` regenerates both byte-identically (`git status` clean afterwards). claims.py's only delta is main's 76 -> 78 entity count.
3. `dev/programme/carries/carry-1922.json`: valid JSON. The diff against main-base is +7/-0, so every main entry is kept and the RCA-1990 entry is present. RO-8's R9-RO-9 carry entry is unchanged from 46b9b4fd.
4. `tools/audit/seat/tmp_paths.py`: keeps #2012's `(?:docs|dev/governance)/decisions/` and adds RO-8's `dev/audit/harnesses` scan scope and `dev/audit/(rounds|waves)` exclusion. The self-test pins both.
5. Per-file three-dot diffs (hunk line numbers normalised) at 46b9b4fd (base f060cb4c) and at the head (base 45142cc3): name-status lists 1685 vs 1686 entries. The only new entry is `R098 tools/audit/harnesses/eg_b7_seam_hubs.py -> dev/audit/harnesses/eg_b7_seam_hubs.py`. Changed patches are limited to the conflict files above, plus `tools/audit/round4/D6/claims.md` (the delete side of item 2). `tests/closures.json`'s patch is identical to 46b9b4fd's, which is how the missing entry follows.

## Cheap checks at head (venv-ci Python 3.14.7, Node 20.10.0, Darwin arm64)

- RESULT tests/layout.py rc=0
- RESULT tmp_paths.py --check rc=0 (0 refused, 0 stale allow entries)
- RESULT closure.py selftest rc=0 (ALL 33 closure shrink pins PASSED)
- RESULT structure.py rc=0 (STRUCTURE RATCHET PASSED)
- RESULT entities.py rc=0 (ALL 2198 ENTITY CHECKS PASSED; needs PYTHONPATH=tests/hastub)
- RESULT policy_lint.mjs rc=0

## CI

`check-runs` at the head: total_count 0. `actions/runs?head_sha=`: 0. The PR is DIRTY, so CI cannot run. There are no reds to answer and no CI evidence to cite.
