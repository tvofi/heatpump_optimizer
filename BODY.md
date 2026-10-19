R10-PREPR-UNPINNED-RED. `tools/pr/prepr.sh` now refuses before the push two things that reddened only in CI: a body whose `## Red checks` omits `mutation` while step 6d lists an unpinned added mutation site (found on #2435), and a raw `git init` or `git clone` in a tracked script (folded in from R10-CI-LAYOUT's carry 1; `governance.yml` runs the same check).

Mechanism: `body_line` takes the file step 6d already writes the unpinned site keys to; a non-empty file adds `mutation` to the `--red` names `policy_lint.mjs --pr-body` is given, so the refusal is the red gate's own sentence. New step 6f, `throwaway_line`, runs `python3 -I tests/throwaway_git.py --check` in the tree. Alternative rejected: a second `## Red checks` parser in the shell, which would be a parallel mechanism that drifts from `policy_lint`.

## Head

`dcf20edf0ac284ae6c011efeff17b65ab923ff98` (code head: `origin/main` merged in at 515f13164, then a one-row reword; measured 2026-10-19).

## Mutation proof

Each mutant is a copy of `tools/pr/prepr.sh` at the head with one predicate line replaced, run as `bash <copy> --self-test` from the worktree:
- `reds+=(mutation)` in `body_line` replaced by `:` : FAIL `an unpinned site with a body whose ## Red checks omits mutation is refused before the push` and FAIL `and the refusal is the red gate's own, naming mutation`.
- the `python3 -I tests/throwaway_git.py --check` call in `throwaway_line` replaced by `out=ok; r=0` : FAIL `a raw repository build in an instrument self-test is refused`, FAIL `and the refusal names the file, the line and the helper`, FAIL `and the ok line is the check's own, so it ran`.

Control: an UNMUTATED copy run the same way (`cp tools/pr/prepr.sh <copy>`) fails exactly one row, `a change to prepr.sh owes the self-test`, which both mutants also print; it is the copy's path, not the mutation. The head's own run has no FAIL row.

## Null control

- Plant: an unpinned site with a body naming no `mutation` red is refused (rc 1, `mutation` ... `does not name it`). Same site with `mutation-answered.md` passes (rc 0). A diff with no unpinned site (empty site file) and a caller passing no site file both pass with the silent body. An unpinned site does not answer a budget raise (both reds owed, rc 1).
- Plant: a raw `git init -q` committed into `tools/audit/probe_selftest.sh` of a shared clone is refused with `REFUSE tools/audit/probe_selftest.sh:3`. The unplanted clone passes the check's own tally line (`0 ... site(s) refused, 0 stale allow`). A tree with no `tests/throwaway_git.py` skips (rc 3), never refuses.
- Call sites: two self-test rows read the main flow, so a step that stopped calling `throwaway_line` or stopped passing the site file fails.

## Figures

- Self-test at the head: `bash tools/pr/prepr.sh --self-test` ends with a line matching `[0-9]+ passed, 0 failed`; the count is the instrument's and is not restated here.
- Unmutated tree passes the real check: `python3 -I tests/throwaway_git.py --check` prints a tally of 0 refused sites and 0 stale allow entries at HEAD (run after the commit: the check reads the committed tree, and the first head's own self-test lines were refused by it, which is why the plant is now spelled in halves).
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run`; changed files are `tools/pr/prepr.sh` and the new fixture `tools/policy/fixtures/policy-rot/prepr/mutation-answered.md`.
- `python3 tools/audit/seat/ref_privacy.py --check` at the head ends `0 refused`.
- `python3 tests/structure.py` ends `STRUCTURE RATCHET PASSED`.

## Red checks

`instrument-self-tests` was red on #2447's first head: `ref_privacy --check` read a self-test row of this diff (a string with `git` before `push`) as an unregistered push site. Fixed in this head by rewording the row, no suppression. Cheaper detector: `python3 tools/audit/seat/ref_privacy.py --check`, which takes seconds and is not in prepr; the standing cost is one more step there, left to R10-CI-LAYOUT's decision. Carry: R10-CI-LAYOUT.

`nightly-status` is main's red (last night's record-autofix), not this branch's: this diff touches no nightly record.

## Forward-carry

- Step 6f reads the committed tree (`git grep` at HEAD), as CI does; an uncommitted raw `git init` is invisible to it. A seat running prepr before committing gets a green it did not earn. Carry: R10-POLICY-FIXER-MD (fixer.md step 6, commit before prepr).
- An unpinned site is now a body obligation at two stages: `## Unpinned sites` (step 7d) and `mutation` under `## Red checks` (this change). If `mutation-autofix` pins the site after the push the `mutation` line becomes a stale claim in the body. Carry: R10-BRIEFS-FOLD (ci-autofix.md: the reviewer re-checks the line after the autofix commit).

## Friction

- fixer.md#6: contradiction: the brief says hand off with tools/audit/seat/handoff_push.sh, which opens or updates the PR and writes the delivery row, and also says make no GitHub writes; I pushed the code head to handoff/r10-prepr-unpinned-red and the body with seat/body_push.sh. Carry: R10-POLICY-FIXER-MD.
- tests/throwaway_git.py#check: cost: it greps the repository it lives in, tools/pr/prepr.sh included, so a fixture owes a shared clone of the real tree (a hand-built tree reads every allow entry stale) and a planted line owes spelling in halves; the first head failed its own step 6f on four self-test strings. Carry: R10-CI-LAYOUT (the tests/throwaway_git.py docstring).
