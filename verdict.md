Fix review: blocked 1a1da73c912e471b40b7b06ea94a76b71d62c100 mutation-vacuous: write_roster passes base_text to lint_gate unpinned (deleting it fails 0 of 254 checks); refusal_tail row passes on the old tail

bus-nonce: 66f4fd376849148b08ff1ca61479c44d

Round: first round of fix review for PR #3344 (R10-ROSTER-WRITE-SWEEP part 2), head 1a1da73c912e471b40b7b06ea94a76b71d62c100, merge base 996ded2a6dc52816bd4c7dd873c048d85fc6adad. I worked in a detached worktree at the head.

## Block

- mutation-vacuous: P435 (carry 20) is wired into the write path by one changed production line, `ok, detail = lint_gate(checkout, lint_cwd, path, base_text)` in `write_roster` (tools/audit/seat/roster_edit.py). I reverted it to the old call `lint_gate(checkout, lint_cwd, path)`, which restores the old whole-roster gate on every real write, and `roster_edit.py --self-test` still passes 254 of 254 (ev/mut2.txt, M8 SURVIVED). The five new `lint gate:` rows call `lint_gate` directly. No row goes through an op. The brief's failing test first was "a roster whose not-done brief cites a shifted line admits an unrelated set-resume", and no such row exists, so nothing pins that the fix reaches a write. Owed: an op-level row, e.g. `set-resume` on a planted roster whose base already carries an ERROR, landing rc 0 with the WARN, with the M8 mutant killed. Its null is the same op adding a new bad citation, refused rc 3.
  Carry: R10-ROSTER-WRITE-SWEEP
- mutation-vacuous: in roster_queue.py, `refusal_tail` is unpinned. I made it ignore the gate banner (M13) and also restored the old `_run_op` tail expression (M14). Both survive, and roster_queue passes 55 of 55 (ev/mut1.txt). The row `refusal_tail: a lint-gate refusal reports the ERROR line, not only TOTAL` uses a fixture whose ERROR line already sits in the last three lines, so the old code passes it too (ev/tail_demo.txt, "old tail already names ERROR: True"). On real `write_roster` refusal output the old tail does not name the ERROR and the new one does (ev/tail_demo.txt). So the production change is real but its test is vacuous. Owed: a fixture in `write_roster`'s real refusal shape, i.e. banner, ERROR lines, `CARRY:` line, blank line, `TOTAL`, then `the commit is local ...`.
  Carry: R10-ROSTER-WRITE-SWEEP

## Findings

- Follow-up: `update-ref refs/remotes/origin/<branch>` after a successful push (P409 part b) is unpinned. I replaced it with a no-op rev-parse (M3) and it SURVIVED. The row `P409: two ops in one run both land after our own push` also passes through `_on_origin`'s fetch-on-miss, so the update-ref only saves one fetch. Either pin it with a row that counts fetches, or record it as equivalent in `## Unpinned sites`. The body does not list it there today.
  Carry: R10-ROSTER-WRITE-SWEEP
- Follow-up: postmerge.py's call site `last = refusal_detail(o)` is unpinned. I restored the old last-line expression (M16) and it SURVIVED. Only the helper is unit-tested.
  Carry: R10-ROSTER-WRITE-SWEEP
- Follow-up: in roster_queue `_run_batch`, the `mark_line(a.queue, ln, "refused")` for a parse-refused line is unpinned (M12 SURVIVED). Without it, under `--mark` a malformed line stays unmarked and is re-run every pass. Also, when a later batch-level failure falls back to the single-op path without `--mark`, the malformed line is reported refused a second time, because the fallback re-runs the whole range. That is minor, but the self-test does not cover it.
  Carry: R10-ROSTER-WRITE-SWEEP
- Follow-up: the body's mutant_run.py figure, "11 SURVIVED, 0 KILLED", is self-declared untrusted and undiagnosed. My hand mutants M2, M4, M5, M6, M7, M15, M1, M9, M10 and M11 kill, so the runner's zero is an instrument result, not a fact about the diff. I did not re-run it (fix-review.md 11: CI's heavy runs are cited, not re-run).
  Carry: dismissed: the body discloses it as untrusted and the hand mutants in this verdict supersede it

## Evidence

- RESULT self-tests at the head: roster_edit 254 checks, 0 failed; roster_queue 55 checks, 0 failed; postmerge 18 checks, 0 failed. These match the body's figures.
- RESULT mutants (ev/mut.py, ev/mut1.txt, ev/mut2.txt). Each mutant was applied, the owning self-test run, and the line restored; `git status` was clean afterwards.
  - KILLED: M1 (--add store), M2 (_on_origin no fetch), M4 (empty base set), M5 (pass every error), M6 (drop whole-check), M7 (no WARN), M9 (keep the refused line), M10 (no per-line catch), M11 (no batch-failure report), M15 (refusal_detail ERROR lead).
  - SURVIVED: M3, M8, M12, M13, M14, M16.
  - The body's four named mutants (carries 17 to 20) reproduce as killed.
- RESULT real brief_lint.mjs end-to-end (my own harness, disclosed: ev/e2e_real_lint.py, ev/e2e_real_lint_out.txt). I planted two errors in a roster copy from handoff/audit-r10-roster and called `lint_gate` with origin/main as lint_cwd:
  - An unrelated write beside them passes, with WARN lines naming the group.
  - A new bad citation in a live group (R10-PREPR-CAP) is refused, naming it. So is one in the same group.
  - A clean roster gives TOTAL 0.
  - With no base text, the old gate refuses.
  - brief_lint prints one line per error (`  ERROR   [group] kind: message`), so `_lint_errors`' `whole` check holds on the real format.
  - A repeated identical bad citation is deduplicated by the lint, so it passes as pre-existing. That is the brief's key semantics, not a defect.
- Finder's harness: the group's controls are the self-test rows the carries name; no committed finder harness. The packet names none. The e2e harness above is mine.
- CI: `merge_train.py classify 1a1da73c912e471b40b7b06ea94a76b71d62c100 --pr 3344` printed `GREEN 1a1da73c912e471b40b7b06ea94a76b71d62c100 pending: none red: none` (ev/ci_classify.txt). The packet's gate digest has no failure on any page, so the body's `## Red checks: none` matches.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 against both 996ded2a6d and origin/main at 17e621f08 (tree 8188e7a5). No conflict.
- Head: `git ls-remote` shows the branch is still at 1a1da73c; the body's `## Head` names it.
- Untouched: VERSION, the manifest, RELEASE_NOTES.md and tests/ are all untouched in the three-dot diff. The delivery row dev/programme/delivery/3344.md is in the diff.
- Size: 4 files, +200/-27, under the 400-line split bound.
- Architecture: `score.py --diff 996ded2a6d 1a1da73c` gives `Architecture score: dS +0.0000 NULL`.
- Structure: `tests/structure.py` printed STRUCTURE RATCHET PASSED; no budget file is in the diff.
- tests/entities.py, run plainly: rc 1, `ModuleNotFoundError: No module named 'homeassistant'` from tests/harness.py (ev/entities_tail.txt). This is an environment failure in this container, not a result about the diff; the CI `tests / closures` and `closure-scope` lanes are green at this head.
- Carry audit of carries 0 to 16: I checked the build of 17 to 20 (P409, P417, P418, P435). I did not re-derive the body's "91 of 342 groups" handoff_push figure for carry 9. It is not verified here, and it is a roster-data residue already moved to R10-CARRY-RESIDUE-2.
- Forward-carry: the body says none. The block above returns to this same group.
