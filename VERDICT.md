Fix review: merge 36143360cea1d1076d917daa23898e0590a73872

bus-nonce: 616ec1e743856a99058a7504912a898a

Round 2 (delta re-check after round 1's `blocked 212415bd07b47976920f7d4a05594a16a471f4e8 mutation-survivor`). I measured at head `36143360cea1d1076d917daa23898e0590a73872` from a detached worktree at that SHA. Merge base = origin/main = `78dd34354e8300bdff2f660db9cc778ab4a9e4d7`. Contract: dev/governance/roles/fix-review.md at origin/main; `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. `review_carry.py 212415bd 36143360cea1d1076d917daa23898e0590a73872` printed FRESH-REVIEW, so this is a full re-review of the delta. The harness is the finder's: the round-1 reviewer's `evidence/mut.py` and `evidence/mut2.py` from `verdict/3153`, run unchanged.

## Findings

- The body's `## Red checks` still names the round-1 head `212415bd` and says "No CI has run yet at this round's new head". Its `git diff --stat` and merge-base figures (`7f849a249`, 1 file) describe the handoff `ebb90ba9`, not the live head, where the three-dot diff has 2 files (the bot, plus the delivery row restored by the opener's merge). Nothing is owed: at the live head none of the 55 check-runs concluded red, and `pr-contract` passed after the last run concluded. Carry: dismissed: stale wording only; the live head has no red check and the figures hold at the head they name
- Mutant append-on-non-refusal (`return "skip-pins-unread" + claim_refusal(driver_err)`) still survives. It is equivalent, as round 1 recorded: that branch is reached only when `"refused" not in driver_err.lower()`, and `claim_refusal` then returns ''. Carry: dismissed: equivalent mutant, no behaviour change is reachable

## Evidence

- RESULT clean head: `python3 tools/pr/merge_main_bot.py --self-test` printed `merge_main_bot self-test: 48 checks, 0 failed`. Round 1 was 46; the 2 new checks are the two decide rows. ev/selftest-clean.txt.
- RESULT finder's mutants at the head (ev/mutants.txt), each applied, run and restored; `git diff --quiet` printed RESTORED.
  - wrong-line-drop-first: `48 checks, 1 failed`, KILLED. The failing arm is the claim-relay arm, through its new `relayed.startswith(f"{CLAIM_REFUSED}{cf}")` (ev/which-failed.txt).
  - append-on-other-conflict: `48 checks, 1 failed`, KILLED. Only the claim-refusal row fails. Its null-control twin (empty driver_err) stays green under the mutant, so the control discriminates (ev/which-failed.txt).
  - The previously killed mutants stay killed: prefix-mismatch 1 failed, indent-dropped 1 failed, always-append 4 failed, never-append 1 failed, wrong-line-first-only 1 failed, decide-no-call 1 failed, any-to-all 1 failed, body-M3-refused-anywhere 3 failed.
- The new rows are behavioural. One calls `decide(...)` and compares the exact returned string. The other extends the arm that runs the real `tests/env_drift.py --merge-claim-file` driver in a throwaway repo. Neither is a text grep. The figures match the body: 48/1 failed for each mutant, 48/0 at the head.
- RESULT delta: `ebb90ba99` has a single parent, `1e1d346b2` (the round-1 code head). `git diff 1e1d346b ebb90ba9` is `tools/pr/merge_main_bot.py | 9 +++++++++`, all inside `self_test()`. `claim_refusal` and `decide` are unchanged, so the body's "9 inserted lines" holds. `git diff 212415bd 36143360cea1d1076d917daa23898e0590a73872 -- tools/pr/merge_main_bot.py` is the same 9 lines. The three dismissed round-1 items (UTF-8 decode, uncapped relay, and the equivalent skip-pins-unread mutant) touch no changed code, and the body's three Forward-carry items are unchanged. ev/delta.txt.
- RESULT the merges add nothing of the branch's own code. `git merge-tree --write-tree ebb90ba9 origin/main` gives rc 0, and the head's diff against that tree is only `dev/programme/delivery/3153.md` (+1). That is the PR's own delivery row, which the opener's merge of ebb90ba9 into the previous head kept; ebb90ba9's tree has no row. `git merge-tree --write-tree origin/main 36143360cea1d1076d917daa23898e0590a73872` gives rc 0, with no conflict and no MERGE-CLAIM line. ev/mergetree.txt.
- RESULT three-dot diff: `dev/programme/delivery/3153.md` +1 and `tools/pr/merge_main_bot.py` +89/-2. The delivery row is present ("open", R10-996-RUNNER-CLAIMS part 3).
- RESULT these are byte-identical to origin/main: `tests/golden/claimed_drift.txt`, `tests/golden/card_claimed_drift.txt`, `VERSION`, `custom_components/heatpump_optimizer/manifest.json` and `RELEASE_NOTES.md`. ev/standing.txt.
- RESULT `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0. ev/structure.txt.
- RESULT scoped gate: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`. This is a branch mode line, not FULL. The bot's self-test runs in `governance / instrument-self-tests`, which is green at this head. ev/scope.txt.
- `## Head` names the live head `36143360cea1d1076d917daa23898e0590a73872` and the handoff code head `ebb90ba992cff355674d5cf24d844722eee93914`.
- RESULT CI on this head: `merge_train.py classify 36143360cea1d1076d917daa23898e0590a73872 --pr 3153` printed `GREEN 36143360cea1d1076d917daa23898e0590a73872 pending: none red: none` (rc 0, 2026-11-02T01:06:27Z). ev/classify.txt.
- All 55 check-runs (one page) show no concluded failure, cancelled or timed_out. `gate`, `pr-contract` and `tests / mutation` succeeded. ev/check-runs.txt.
- Not re-run by me: the architecture score (`dS +0.0000 NULL` in the body). `arch-score` is green in CI at this head.
- Finder's harness: no committed harness exists for this carry. Round 1 already recorded that the mutant scripts are the round-1 reviewer's own. I reused them unchanged (ev/mut.py, ev/mut2.py) and added my own `which.py`, which names the failing arm.
- The head was re-read before returning: the branch `fix/r10-996-runner-claims-3` is still `36143360cea1d1076d917daa23898e0590a73872`.
