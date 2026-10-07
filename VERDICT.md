Fix review: blocked 82f2641aa964dfcc4f9a16ac4c242a70ec6d7577 body-false: line 37 still says no closures.json entry names eg_b7_seam_hubs.py and git grep returns only the file; at head closures.json:3578 names it

bus-nonce: 0aa9ab562459b0caeb9e099b1a4ccd90

Round 4. Rounds 1-2 ended in `merge` at 46b9b4fd. Round 3 blocked baadb840 on the missing inert_reads entry. This round judges only the delta baadb840..82f2641a, which is the merge of origin/main e0f0b6fb (#2022) in 07c77ee3 plus the one-line fix in 60c00052. The tree of 82f2641a equals the tree of 60c00052. The live head when posting is 82f2641aa964dfcc4f9a16ac4c242a70ec6d7577, MERGEABLE. `git merge-tree --write-tree origin/main HEAD` returns rc=0.

The code is correct and CI's closures job is green. The verdict is blocked only on a body sentence. The body lives on a separate ref, so the fix needs a `body_push.sh`. It does not need a new code head.

## Blocking finding: body line 37 was not corrected

Body line 37 still reads: "No `closures.json` entry and no harness README row names it: `git grep -n eg_b7_seam_hubs` returns only the file itself." At the head, `git grep -n eg_b7_seam_hubs HEAD` returns two hits: the file's usage line and `tests/closures.json:3578` (evidence `grep_eg_b7_at_head.txt`). That contradicts line 39 of the same body. Round 3 named this line, and the fixer claims to have corrected it. The `handoff-body/r9-ro-8` tip b3d7c8f8 has the same text.

Required fix: change the line 37 clause to say that `inert_reads["tests/harness_headers.py"]` names it at `dev/audit/harnesses/` (see the closures bullet) and that no harness README row names it. The fix is body only.

## The fixer's claims, checked

- Main merged: RESULT merge-base(origin/main, head) = e0f0b6fb = origin/main. #2022's 042b66fa is in the history.
- Old path replaced with new path: RESULT `inert_reads["tests/harness_headers.py"]` has 527 entries, contains `dev/audit/harnesses/eg_b7_seam_hubs.py` and does not contain the `tools/...` path.
- Three-dot PR diff at both heads: RESULT name-status is 1686 entries at baadb840 (base 45142cc3) and 1686 at the head (base e0f0b6fb), and the two lists are identical. RESULT the only file whose patch differs (hunk headers normalised) is `tests/closures.json`, and it differs by exactly `- tools/audit/harnesses/eg_b7_seam_hubs.py` / `+ dev/audit/harnesses/eg_b7_seam_hubs.py`.
- No missing paths: `closure.py prune` checks `closures` only, so it cannot support the inert_reads half of this claim. I wrote my own script that applies `closure._is_real_file` to both tables. RESULT closures missing-path entries 0; inert_reads missing-path entries 0. Control: with the old path planted in memory, the script counts 1. The script is my own, not the fixer's (`missing_paths.txt`).
- Stand-in, which I reproduced: I reused round 3's Darwin recording `rec_hh` (taken at baadb840) and `mkstandin.py`, and ran `closure.py check --in-dir <arm> --partial`:
  - RESULT head, standin_eg_b7 rc=0; standin_control rc=0
  - RESULT perturbed head (entry set back to the `tools/` path), standin_eg_b7 rc=1 `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: dev/audit/harnesses/eg_b7_seam_hubs.py`; standin_control rc=0. The perturbation was restored with git checkout.
  - RESULT standin_oldpath at head rc=0. An injected read of a path that does not exist is not flagged, which matches round 3's PHANTOM-guard note.
- Body lines 39 and 71 are corrected and accurate. Line 37 is not (see above).

## CI at 82f2641a (check-runs API)

- RESULT `closures` completed **success**, run 37648625296 job 112885974811, 16:01-16:46Z. It re-recorded `tests/harness_headers.py` on Linux with strace (16:36-16:39, exit 0), then printed "lists 2 file(s) this run did not touch (safe: over-scoped)" and "committed closures cover every file this run touched" (`ci_closures.log`). This is the authority, and it is green.
- `closure-scope` success. `delivery-status` and `nightly-status` failure: per the dispatch these are main's, and on main's push they are skipped. `budget-raise-gate`: one cancelled twin (check-run 112885821312) beside a successful run 37648625777. The orchestrator should rerun the cancelled twin if the ruleset keys on it. CodeQL neutral.
- Still in progress at posting time: `fast (3.14)`, `coverage`, `browser`, and CodeQL `Analyze (python)`. The delta is one JSON line and these do not bear on it, but they are not yet read.
- Red-check trigger: no gate check went red that the delta can reach.

## Cheap checks at head (venv-ci python3, one at a time)

- RESULT tests/layout.py rc=0 (layout self-test: ok)
- RESULT closure.py selftest rc=0 (ALL 33 closure shrink pins PASSED)
- RESULT structure.py rc=0 (STRUCTURE RATCHET PASSED)
- RESULT entities.py rc=0 (ALL 2198 ENTITY CHECKS PASSED, PYTHONPATH=tests/hastub)

## Non-blocking notes

- The new entry was placed where the old one was, so `inert_reads["tests/harness_headers.py"]` is no longer sorted: `dev/audit/harnesses/...` sits after `dev/programme/...`. Main's list is sorted, and round 3 asked for sorted position. All consumers use sets, so this is cosmetic. Moving it while fixing the body would cost a new code head, which is the fixer's choice.
- Body line 69 still quotes `ALL 2191 ENTITY CHECKS PASSED` "at the head above". Line 36 and my run both give 2198. The figure comes from an earlier round and is stale. Fixing it with line 37 is recommended.
