Fix review: blocked 0a02619939e72e83cd52702aaf319e98049c4ba9 selftest-scope-ungated: the new governance.yml step 'Show the figure-block renderer refusing its own fixtures' uses `if: ${{ !cancelled() }}`, so governance / instrument-self-tests is red at this head

bus-nonce: e7b962b6ace004193dd70c45ab7de058

## Block

`governance / instrument-self-tests` (job 129141009751) concluded failure at this head. Log tail: `FAIL the live job parses (115 steps) and its gating is consistent` / `selftest_scope self-test: 90 checks, 1 failed`. Reproduced locally in a worktree at the head: `python3 -I tools/ci/selftest_scope.py static` prints `UNGATED step 'Show the figure-block renderer refusing its own fixtures': its if: does not read steps.scope.outputs.<its own id>`; the same self-test on origin/main prints `90 checks, 0 failed`. So the diff causes it. Every other step in that job reads `steps.scope.outputs.<id>`; this one needs a scope id registered in tools/ci/selftest_closures.json (see tools/ci/selftest_scope.py) and an `if:` that reads it.

The body's `## Red checks` names only `governance / delivery-status`; it does not name this red. `governance / instrument-self-tests` is not in `merge_train.py owed-reds` (that listing has `tests / arch-instrument` and others), so this is not a root-cause-trigger block; it is blocked as a real red the diff caused, which would also turn the main push (forced FULL) red. Cheaper detector: `selftest_scope.py static` runs in seconds and is in no prepr step (`git grep selftest_scope tools/pr` is empty), so the fixer cannot have seen it before the handoff.

## Findings

- Surviving mutant: deleting the base-overlay line `_git(wt, "checkout", base, "--", f)` in `run_instrument` leaves `figure_block.py --self-test` at `11 checks, 0 failed`; every registry entry the self-test builds has `"files": []`, so nothing pins the property the header and body claim (the program is the base's, the tree is the head's). Needs a check whose registered instrument has a `files` entry that the head modifies and whose output differs. Carry: dismissed: fold into the re-cut of this PR, which owes the fix above anyway
- Residual: `pr-contract` runs `python3 -I tools/pr/figure_block.py verify` on the head's checkout, and `scope-line`/`structure-ratchet` execute `tests/closure.py` and `tests/structure.py` (base copies overlaid) which import head modules from the head's tree; the overlay covers only the listed files, so the base-program guarantee is partial. Judge whether that is within the card-7 ruling. Carry: dismissed: design observation for the owner, not a defect this PR claims to have closed

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main 0a026199...` exits 0, tree 9d58cd0aa822ab0f53229479236badc32e611757; no conflict.
- `python3 -I tools/pr/figure_block.py --self-test`: `figure_block self-test: 11 checks, 0 failed` at the head, matches the body's figure.
- Mutants on figure_block.py at the head: `if body != want:` -> `if False:` fails 1 (hand-typed value); stale head/mb check -> `if False:` fails 2; `if name not in reg:` -> `if False:` crashes the self-test (no summary line, KeyError); overlay checkout removed: survives (finding above); `ok_rc` check removed: survives, but an empty output is then still refused (`printed nothing`), so it is near-equivalent for the `bad` fixture.
- `bash tools/audit/seat/body_push.sh --self-test`: `38 checks, 0 failed`, including the `MUTANT refresh deleted` arm. `node tools/policy/policy_lint.mjs --self-test`: `FIXTURE ok`.
- Review packet: refusals none, advisories none, `CARRY-AUDIT: 0 finding item(s)`, `FIGURES: 8 resolved, 0 not verified, 0 refused`.
- CI at read time: instrument-self-tests failure (above); `tests / closures`, `coverage`, `fast (3.14)`, `arch-instrument` and `codeql / Analyze (python)` still in progress; all other checks success or skipped. `merge_train.py classify` printed `WAIT ... pending: gate red: none` (rc=3) on each poll, since it does not list this non-required red.
- Not examined: the figure-block mutation of the pr-contract wiring and `prepr.sh` step wiring beyond their own self-test arms; VERSION/manifest/notes untouched per the packet's three-dot diff (no such path in the diff). Round: first review by this seat.
