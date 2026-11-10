Fix review: merge 825f5492709accfd80792fcf151f1459b0dca554

bus-nonce: f64e2c5aa2e1eedcd0f39fe028cd9e25

## Scope

Delta review, a later round (the prior verdict at 54f76620231dab81bc2111b87bebacfaf78992cc was blocked on main-conflict alone). Reviewed: `git diff 54f76620231d..825f5492709a`, the branch's own diff (three-dot against origin/main) before and after, and the hand-resolved conflict. The branch changes nothing under `custom_components/`, so the scope does not widen.

## Prior finding

- main-conflict on `dev/audit/harnesses/r10_codescan_wait_race.py`: resolved. `git merge-tree --write-tree origin/main 825f5492709a` exits 0 against origin/main b07627250 (ev/merge_tree.txt, only `LEDGER-MERGE: resolved tests/closures.json`).

## Evidence

- RESULT merge-tree rc=0 vs origin/main b0762725099f.
- The merges since 54f766202: e0d381a29 merged origin/main 7bdc8aa2e. Re-merging its parents with `git merge-tree` reproduces the one conflict; the committed tree differs from the auto-merge only in `dev/audit/harnesses/r10_codescan_wait_race.py` (ev/remerge.txt). 7b2b7cb79's tree equals e0d381a29's. 825f54927's tree equals the clean auto-merge of its parents (7b2b7cb79, b8f67a775) byte for byte: no hand edits.
- The branch's own diff before and after (ev/own_prev.diff, ev/own_head.diff, ev/own_diff_delta.txt): the only changed hunks are in the harness's selftest. Main's `caught()` helper now carries the page checks, the over50/many1760 cases go through it, and the summary keeps main's accounting `len(want) + 4 + len(pg)`. The other change is one context line in `tests/closures.json`. `pages()` itself (the MAX_ITEMS bound) is unchanged since 54f766202.
- RESULT harness head 825f5492709a: `selftest: 17 checks, 0 failed` rc 0. The body's head figure matches.
- RESULT harness prior head 54f766202: `selftest: 14 checks, 0 failed` rc 0. The count moved by main's accounting (3 checks), and no check fails at either end.
- RESULT mutant M1, the loop bound reverted to `range(1, ghapi.MAX_PAGES + 1)`: `17 checks, 1 failed pages['many1760']` rc 1, killed. The body's 14-check figure predates the merge, and the body says so.
- RESULT mutant M2, the 5xx fallback removed: `17 checks, 3 failed pages['fallback', 'over50', 'many1760']` rc 1, killed.
- RESULT null control, the unmutated file re-run after restore: `17 checks, 0 failed` rc 0 (ev/harness_runs.txt).
- The body's `## Head` names 825f5492709a, the head measured here. Nothing in the delta touches VERSION, the manifest version or the RELEASE_NOTES heading.
- review_packet.py did not render: `UNAVAILABLE: git merge-base --is-ancestor 42454528717 origin/handoff/audit-r10-roster: fatal: Not a valid object name 42454528717`. It reads 42454528717, an Actions run id from the body, as a commit. No packet was written, so the live checks were read directly.
- CI: `merge_train.py classify` returned WAIT (pending: gate, red: none) from 02:25Z to 03:33Z. From 03:34Z it exits 2: `REFUSE ci: the check runs at 825f5492709a could not be read`. The head now has 101 check runs, and `gh api --paginate` follows page 2's Link URL in the `repositories/<id>` form, which this session's proxy refuses (`Numeric-ID repository paths ... (HTTP 403)`). This is an environment read limit, not the head. The required set was then read with explicit `page=` reads (ev/required_checks.txt), against `merge_train.py owed-reds` (ev/owed_reds.txt, 23 contexts).
- RESULT required checks at 825f5492709a, read 04:05Z: all 23 owed contexts completed, 0 red, 0 pending. The latest `gate` (run 42748431595, workflow_dispatch "CI code pr=3361", 04:03Z) is success, and so is `pr-contract / pr-contract` (04:02Z). The earlier code run 42741640648 also ended with a green gate (03:16Z).
- Two earlier `gate` reds at this head, jobs 129592117484 (run 42741641810) and 129592948245 (run 42741776759), are edit-run deferrals. Their logs end `FAIL run(s) [42741640648...] at this head are still being judged; their gate decides`, and that code run's gate then went green. A `pr-contract` run that started after the last of them concluded (04:02Z) is green, and per fix-review step 11 that run is the evidence.
- The non-required reds `governance / instrument-self-tests` (runs 42741640648 and 42748431595) are outside `owed-reds` and block nothing; their cause is under `## Findings`.

## Findings

- governance.yml's step `Show the workflow read runner refusing its own fixtures` (added by this PR) has `if: ${{ !cancelled() }}` and no `id:`, so `tools/ci/selftest_scope.py static` reports `UNGATED step ...: its if: does not read steps.scope.outputs.<its own id>`, and its self-test fails `the live job parses (118 steps) and its gating is consistent`. On this head's CI, `governance / instrument-self-tests` (job 129586577926) is red on `selftest_scope self-test: 103 checks, 1 failed`, and `selftest_scope_mutants.sh` then reports `BASELINE RED` (ev/instrument-self-tests_tail.txt). origin/main b07627250 alone passes (`103 checks, 0 failed`). The same problem shows at 54f766202 and e0d381a29 (ev/selftest_scope_static.txt), so it is not a new regression from the merges. `instrument-self-tests` is not in `owed-reds`, so under the owner's red-check ruling it does not block. Once merged, it turns main's instrument-self-tests red until the step gets an `id:`, a `steps.scope.outputs.<id>` gate and its `tools/ci/selftest_closures.json` record. The orchestrator should land that before or with this merge. Carry: #2731
