CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-card-collapse, at head b55fc8eb5bfce6a3c2022314116d0b19d1a901e6. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch b55fc8eb5bfce6a3c2022314116d0b19d1a901e6 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-card-collapse before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-card-collapse, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-card-collapse, even with no code. Then push the code to refs/heads/handoff/r10-card-collapse, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-card-collapse <body.md>`, which pushes refs/heads/handoff-body/r10-card-collapse; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-card-collapse`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-card-collapse and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-card-collapse and refs/heads/handoff-wip/r10-card-collapse-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
REPAIR ROUND 1 for R10-CARD-COLLAPSE (size M), pull request 3441, head b55fc8eb5bfce6a3c2022314116d0b19d1a901e6 (branch fix/r10-card-collapse; handoff/r10-card-collapse d7c39135839ea0a985796105ebfda170cdd6d505 is its ancestor). Continue from the PR head; do not re-cut. Keep the session light: no whole-file prints, capped command output, small pushed handoff-wip commits; BLOCKED.md with the exact question if stuck.

The first review returned BLOCKED, class pin-missing (verdict verbatim below). Your work:
1. Pin both claimed behaviours in tests/card.mjs so the reviewer's mutants R1 and R2 die: fold state across a hass refresh, and focus return to the dialog copy of a header. Prove each with a failing test first and the mutation (the reviewer's R1 and R2 are described in the verdict; re-create them) killed, with the null control.
2. CLASS SWEEP: go through the pull-request body and list EVERY claimed behaviour. For each, name the test that pins it, or pin it, or withdraw the claim from the body. Paste the table in the body.
3. Conflicts: if `git merge-tree --write-tree origin/main HEAD` conflicts, MERGE origin/main into the branch and re-run steps 2-8; never rebase or re-cut.

PREVIOUS VERDICT (verbatim):

Fix review: blocked b55fc8eb5bfce6a3c2022314116d0b19d1a901e6 pin-missing: fold state across a hass refresh and focus return to the dialog copy of a header are claimed in the body but unpinned; mutants R1 and R2 survive tests/card.mjs

bus-nonce: 561e6cbe79fd65fe8438be412ba6ea95
pending-ci: gate

Round: first review (round 1), full scope. Measured head: b55fc8eb5bfce6a3c2022314116d0b19d1a901e6. At post time it is still the tip of fix/r10-card-collapse (git ls-remote).

## Block

- **R1 survives.** The body's design decision says fold state "survives every plan-refresh rebuild". Adding `this._folds = { narrative: false, whynow: false };` to `set hass` (heatpump-optimizer-card.js:15215) resets every fold on each hass update, and `tests/card.mjs` stays green (rc=0, 0 FAIL). No check in the suite sets a second hass while a fold is open. This is the plan-refresh survival the brief asks for. The production code does keep the state: the reviewer probe shows aria-expanded `true,false,true,false` both before and after a fresh hass. The property is just unpinned.
- **R2 survives.** The body says "Focus returns to the rebuilt copy of the pressed header", and the headline renders twice when the dialog is open (4 `[data-fold]` heads). Replacing the index lookup with `this.shadowRoot.querySelector(`[data-fold="${key}"]`)` sends focus to the card copy behind the modal dialog. `tests/card.mjs` stays green. The `collapse: focus returns to the rebuilt header` check clicks only the card copy, with the dialog closed. The browser lane's `cardCollapse` also presses only `ha-card [data-fold]`. The production code is correct: the probe shows a click on dialog copy index 2 returns focus to index 2 of 4. A one-key regression to the obvious selector would pass every lane, though.
- **What clears it.** Two checks in the R10-CARD-COLLAPSE block of `tests/card.mjs`, each re-proved with its mutant (R1, R2 as in `ev/mut_driver.py`):
  1. Open a fold, set a new hass, and assert the fold is still open.
  2. Open the dialog, click the dialog copy of a header, and assert `activeElement` is that copy (index 2 or later) and not the card's.
  Production code needs no change.

## Findings

none beyond the block

## Evidence

- RESULT `PYTHONPATH=tests/hastub node tests/card.mjs` at head: `ALL CARD CHECKS PASSED`, rc=0 (`ev/card_head.txt`; needed `tests/plan_view.py` first, `ev/plan_view.txt`).
- RESULT `PYTHONPATH=tests/hastub node tests/card_drift.mjs`: `card_drift: 44 state(s) moved and claimed, 1 identical`, rc=0 (`ev/card_drift_head.tail.txt`, tail of a 17 MB log). This matches the claim block in `tests/golden/card_claimed_drift.txt`: every rendering state is claimed, and editor_schema is identical. claims-for stays 7.1.10 = VERSION.
- RESULT `python3 tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok` (`ev/claims_only.txt`).
- RESULT `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
- RESULT `python3 tools/audit/archscore/score.py --diff dbd1ab5b0712ebc51e29ef8c001a2c0ef68af3cd`: `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`). This re-derives the body's figure. The `card_clone_copies` 103 -> 108 intermediate is not re-derived, because it was at a superseded head.
- Mutants re-created at the head, each run through `tests/card.mjs` and restored (`ev/mut_driver.py`, `ev/mutants_all.txt`):
  - NULL (comment edit): SURVIVED, as a null must.
  - M1 KILLED (5 FAIL), M2 KILLED (19), M3 KILLED (6), M4 KILLED (1), M5 KILLED (1), M6 KILLED (5), M7 KILLED (2). The killing checks match the body's named checks.
  - Reviewer's own mutants:
    - R3 aria-expanded always "false": KILLED (2).
    - R4 why-now lead picks the weakest driver: KILLED (1).
    - R5 body rendered while folded: KILLED (3).
    - R1 and R2: SURVIVED (see Block).
  - The M4 anchor string occurs twice in the file, so the driver anchors it with the preceding fold-handler line. The first pass was cut off at that assertion (`ev/mutants_firstpass_partial.txt`) and resumed from M4.
- Reviewer probe (`ev/reviewer_probe.txt`, `ev/reviewer_probe_note.txt`): with the dialog open the shadow root has 4 fold heads and no duplicate `id`. This confirms the no-id/aria-controls decision: no duplicate ids in the doubly rendered headline.
- Keyboard: the headers are native `<button type="button">`, so Enter and Space arrive as click. The browser lane's `cardCollapse` checks Enter, then Tab and Space, in light and dark. Not re-run here: no scope selects that lane, and CI's `tests / browser` is cited instead (fix-review step 11).
- docs/dashboard-card.md claims, checked against the code at the head:
  - Folded summaries (the kWh and cost total, else the first line; the strongest driver).
  - Both folds start folded on page load; each toggles on its own.
  - Screen readers hear the expanded state (`aria-expanded`).
  - The chips and footnote appear only in the enlarged view.
  - The why-now driver list (price rank, comfort floor, forecast, mold guard, away) equals the five `whynow.driver_*` keys at card.js:921-933.
  - README and docs/index.html carry the same sentence.
  - All hold.
- `git merge-tree --write-tree origin/main b55fc8eb5bfce6a3c2022314116d0b19d1a901e6`: rc=0, no conflict (`ev/merge_tree.txt`).
- VERSION, the manifest version and RELEASE_NOTES.md are untouched in the three-dot diff.
- CI: `merge_train.py classify` still prints `WAIT ... pending: gate red: none` after more than 40 min of polling at 60 s+ intervals (`ev/classify.log`, `ev/classify.txt`).
  - `tests / nightly-status` is red. It is outside the required set that `merge_train.py owed-reds` prints (`ev/owed_reds.txt`), so it is not this PR's and is owed no answer.
  - The body's `## Red checks: none` is consistent with that.
- There is no finder harness: this is an owner request, and the body says so. The before-and-after is the PR's own `tests/card.mjs` block. Not re-run at the merge base: the base renders no `[data-fold]`, and that is evident from the diff.
