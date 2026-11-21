Fix review: merge e28f4287ee044b0dae5bcb6682ba820f1b3001f9

bus-nonce: c1b81b8f72960167beab0e7aa5be431a
pending-ci: gate

## Scope

Round 4, a delta review (the owner's 2026-11-09 rule) from the merge verdict at `c1ad2ede5308d1a9f25379c88f10502b387b0fb2` (comment 7052086305). `tools/audit/seat/review_carry.py c1ad2ede53 e28f4287ee` answers FRESH-REVIEW: `0850b21ca4 resolves tests/golden/claimed_drift.txt to something other than the union of its parents or main's driver output on them`. Branch-only commits since the reviewed head: `0850b21ca4` (merge of origin/main `053c33bcc6`), `fd6b5de090` (comments in `tests/features.py`), `d3e6982482` and `e28f4287ee` (merges). Detached worktree at the head. `review_packet.py render` refused `UNAVAILABLE: git merge-base --is-ancestor b2ce461c origin/handoff/audit-r10-roster: fatal: Not a valid object name b2ce461c` and wrote no packet, so this review worked without one. I took the scope from the brief and step 12.

The delta is the difference between the two heads' three-dot diffs (`ev/own_R.diff`, `ev/own_H.diff`). It holds only two things. One is the ten comment re-wraps in `tests/features.py`. The other is shifted hunk context in `tests/golden/claimed_drift.txt`, where main's three #3736 claim lines now precede the branch's hunk. The branch's own lines in the claim file are textually the same. No path under `custom_components/` changes in the branch-own diff between the two heads, so nothing widens the review.

## Evidence

- RESULT claim resolution `0850b21ca4` (parents `c1ad2ede53` and `053c33bcc6`, merge base `99436a082c`). The driver on the three versions prints `MERGE-CLAIM: refused tests/golden/claimed_drift.txt` and gives stamps base `10.1.0`, this branch `10.1.0`, incoming `10.1.1` (`ev/driver_stderr.txt`). A hand resolution was therefore owed.
  - The branch side's changes from base are the two claim lines `cycling_cost` and `everything_on`, plus the suspension of their two `# may-drift:` entries, each with a verbatim restore note.
  - Main's changes from base are `claims-for: 10.1.1`, the v10.1.1 note, and the `price_risk`, `start_below_band` and `confidence_margins` claims. Main removed no claim.
  - At the merge and at the head, the claim set equals the union of both parents' claims: five lines, `diff` empty.
  - The `may-drift` set equals main's set minus exactly the two suspended entries (`diff` empty).
  - `git diff origin/main e28f4287ee -- tests/golden/claimed_drift.txt` holds exactly those four branch changes and nothing else, as the body states. Files are in `ev/claim_*.txt`.
- RESULT claim-files.md conditions at the head:
  - `claims-for: 10.1.1` equals `VERSION`, which is `10.1.1` at both the head and main.
  - No fixture is both claimed and may-drift.
  - `python3 tests/env_drift.py --claims-only origin/main` prints `claims hygiene: origin/main ok`, rc 0 (`ev/claims_only.txt`).
  - Planted mutant 1 re-instates `# may-drift: cycling_cost` beside its claim. The check refuses with rc 1, `CLAIMED AND MAY-DRIFT` (`ev/mutant_maydrift.txt`).
  - Planted mutant 2 sets `claims-for: 10.1.0`. The check refuses with rc 1, `STALE CLAIM FILE` (`ev/mutant_claimsfor.txt`).
  - The direction of each claim is stated in its reason (cost up for `cycling_cost`, down for `everything_on`). The body's re-taken figures at `0850b21ca4` are fixture-solve readings that I did not re-derive. `tests / fast`'s `env_drift.py --all` in CI decides them (see CI below).
- RESULT `fd6b5de090` is comments only:
  - Its diff (`ev/fd6b5de0.diff`, 24+/24-) has 0 changed lines that are not `#` comments.
  - `ast.dump` of `tests/features.py` before and after is identical.
  - `python3 tests/comment_ratchet.py --text-only fd6b5de090` and `--text-only HEAD` each print `RESULT code_changed_files=0 line_shifted_hunks=0`.
  - `--base origin/main` at the head prints `long_units_base=1622 long_units_head=1622`, `comment_ratchet: OK`, which matches the body.
  - Mutant: reverting the commit's features.py hunks makes the ratchet refuse, `REFUSE tests/features.py: long units 465 -> 475`, `comment_ratchet: FAIL`. That is the refusal the body quotes (`ev/mutant_comment_revert.txt`).
- RESULT the other merges: re-running `git merge-tree --write-tree` on the parents of `d3e6982482` and of `e28f4287ee` reproduces each commit's tree exactly. Only `0850b21ca4` differs from its git merge, and only in `tests/golden/claimed_drift.txt`.
- RESULT merge with main: `git merge-tree --write-tree origin/main e28f4287ee` exits rc 0 with tree `66541e4de4`, which is the head's own tree. origin/main is `78d3b40221`, the head's merge base.
- RESULT version: the three-dot diff touches neither `VERSION`, `custom_components/heatpump_optimizer/manifest.json` nor `RELEASE_NOTES.md`.
- RESULT body head: `## Head` names `e28f4287ee044b0dae5bcb6682ba820f1b3001f9`, the head measured here.
- RESULT prior findings (round 3):
  - `conflict-claim-file` is resolved as that note prescribed, verified above.
  - `body-stale` is resolved: `## Head` now records the `053c33bcc6` conflict and its resolution.
  - `train-row` is unchanged and not seat-owed.
  - `review-packet` reproduces (the `b2ce461c` refusal above).
- RESULT CI at this head, read from the commit's check runs at about 12:09 UTC (`ev/classify_final.txt`, `ev/classify_log.txt`). `merge_train.py classify` printed `WAIT e28f4287ee044b0dae5bcb6682ba820f1b3001f9 pending: gate red: none` on every poll from 11:40 to 12:10 UTC, about 30 minutes, with exit 3 each time. The runners were backlogged: the jobs sat queued until about 11:43.
  - Completed `success`: `tests / typing`, `tests / arch-instrument`, `tests / closure-scope`, `tests / briefs`, `tests / nightly-status`, `arch-score / arch-score`, `budget-raise-gate / budget-raise-gate`, `governance / wave-script`, `governance / policy-docs`, `hassfest / hassfest`, `validate / validate-hacs`, and the three `codeql / Analyze` jobs.
  - `governance / env-matrix` is `cancelled`. It is not in the `owed-reds` set (`ev/owed_reds.txt`).
  - Still running or queued: `tests / fast (3.14)` (started 12:08:31), `tests / mutation`, `governance / instrument-self-tests`, `tests / coverage`, `tests / closures`, `tests / replay`, `tests / browser` and `gate`.
  - The fixer's local Mac failures in `tests/features.py` and `tests/optimality.py` are not decided at this head: both scripts run in `tests / fast (3.14)` (`tests/run.sh`), which had not finished. `tests / fast`'s `env_drift.py --all` likewise decides the claimed fixtures' movement on the main base that includes #3736. Under `pending-ci` the relay refuses this verdict over a red, so a CI reproduction of either failure stops the merge.
  - No red has been read at this head, so no `## Red checks` answer is owed.

## Findings

- Note: review-packet: `review_packet.py render` again refuses `UNAVAILABLE` on `git merge-base --is-ancestor b2ce461c origin/handoff/audit-r10-roster`. `b2ce461c` is a PR-body forward-carry item hash, not a commit: the roster's `wave-r11-groups.json` line 1933 cites `body item b2ce461c`, and the packet reads it as an object name. This is the second instance on this PR (round 3 recorded the first). Carry: dismissed: a dispatch-side instrument defect reported to the orchestrator with this verdict; at a third instance it is root-cause.md's
- Note: round-count: this is the fourth review round on #3805, and fix-review.md says that from the fourth `fixer.md` owes a re-cut. Rounds 2 to 4 are delta reviews over main merges and a claim-file hand resolution, with no production change since round 2's merge verdict. Whether this counts toward the re-cut is the orchestrator's call. Carry: dismissed: process count named for the orchestrator; no code defect
- Note: ci-pending: `tests / fast (3.14)` had not finished, so this review cannot state whether CI reproduces the fixer's local `features`/`optimality` failures. The `pending-ci` line hands that decision to the relay. Carry: dismissed: decided mechanically by the relay at green or red on this head
