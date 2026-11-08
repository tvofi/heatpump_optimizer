Fix review: merge 54155040edb359e8693efab3cb9791da7d74ac56

bus-nonce: 53bf5aaea099206bbfd7274597e1aaa5

## Round

Round 3 (re-review after the round-1 `claim-refuted` block, comment 6711338489; it is the only prior verdict on the PR). Measured head `54155040edb359e8693efab3cb9791da7d74ac56`, merge base `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76`, three-dot diff only.

## Prior finding, checked at this head

- Round 1: #3219 (`aca500910`) was misfiled into group A. Resolved at this head. Section 3 now puts #3219 in D and cites `tests / mutation` job 127045678304 (04:18:12Z, before the 04:32:06Z verdict), which is what round 1 found. I re-derived the split from the tsv's 18 rows: A 7 entries / 7 PRs (#3167 second, #3181, #3204, #3211, #3217, #3240, #3244 first); B 4 / 4; C 4 entries / 3 PRs; D 3 / 3; 7+4+4+3 = 18. I re-took section 5 from the tsv's fourth column. A without #3211 is 71+187+64+124+80+111 = 637 over 6 = 106.2, P = 7/93 = 0.075, 8.0 min. B is 848/4 = 212, x 4/93 = 9.1 min. C is 1186/4 = 296.5, x 4/93 = 12.8 min. The stated null control (#3219 back in A: 769/7 = 109.9, 8/93, 9.5 min) re-derives. Group D's refusal still holds with #3219 in it.

## Findings

- Section 3, group A: the sentence "Three are a runner killing `codeql / Analyze` or a cancelled gate, one is a closed PR, two are the gate deferring" sums to 6 against the group's stated 7 entries. Its own rows give four: codeql at #3181 and #3217, and a cancelled gate at #3167 second and #3204. The repair introduced "Three" when it decremented the round-1 "Four", which had already been one short of A's 8. No computed figure, state or countermeasure depends on it, so it does not block. It is a figure in a durable record that does not re-derive, and the word should read "Four". Carry: #3156

## Evidence

- Roles: `git diff 4b5d771bd...origin/main -- dev/governance/roles/` is not empty. Main added one sentence to fix-review.md ("Evidence names differ beyond case"). I followed main's copy, and the names under `ev/` differ beyond case. `ev/roles_current.txt`.
- Count re-derived: `node tools/policy/policy_lint.mjs --stats --since v7.1.2 --window-cache ev/W.json`, run from the head worktree, gives `STATS: 108 merged pull request(s)` and `16 / 20 ci-red` (`ev/stats_review.txt`). origin/main has moved past the base. The two extra entries are #3265 and #3273, both merged after `4b5d771bd` (`87082a25a`, `53273de4d`). `entries.py` on that cache prints the record's 18 rows byte-identical as its first 18 lines, plus those two (`ev/entries_review.tsv`). So the record's 14 / 18 at its base stands, and the growth is the window moving, as section 1 says. #3156's body reads 11 PRs / 14 entries at filing, as the record states.
- Reader null control: `ci-redd` gives `ENTRIES 0 PRS 0`. I rewrote #3242's `ci-red` verdict to `ci-redx` in a copy of the cache, and the output moved from 20/16 to `ENTRIES 19 PRS 15` (`ev/null_control.txt`).
- inline_scan re-timed at the head: prints `0`, real 0.769 s (`ev/inline_scan.txt`; record 0.55 s, round 1 0.659 s). That is machine noise. Against B's 547 s the factor is still about 700. The `prepr.sh:436` comment deferring `harness_headers.py` to CI is present.
- Rules 2 and 3 (root-cause.md, defect-root-cause.md): every group has a named cause. B, C and D have states (c), (b) and n/a; A has (d) with the deferral sub-cause stated as not established. The cost test carries numbers. B's countermeasure is owed later with the red/green demonstration named. C is stated as policy awaiting the owner, and nothing of it is applied. A (runner kills) and D carry recorded refusals. The record changes neither the keying rule nor the gate. The three-dot diff touches no file under `.claude/`, `tools/`, `tests/` or `.github/`.
- Body: `Disposes #3156` with no closing keyword. The delivery row `dev/programme/delivery/3295.md` is in the diff. VERSION, the manifest and RELEASE_NOTES.md show 0 diff lines (`ev/threedot_stat.txt`). `## Head` names `54155040e`, which is this head. carry_audit at the head: 3 routed, 0 unrouted.
- Merge: `git merge-tree --write-tree origin/main 54155040e` exits 0, tree `1c793cfdf` (`ev/merge_tree.txt`).
- CI: `merge_train.py classify 54155040e... --pr 3295` gives `GREEN 54155040edb359e8693efab3cb9791da7d74ac56 pending: none red: none`, rc 0, at 03:52:01Z (`ev/classify_final.txt`, `ev/classify_runs.log`). Every check run at this head, read from one 49-run page (total_count 49), concluded success or skipped, with one exception. The edit-kind `gate` job 128613059066 (run 42441205339) concluded failure at 03:28:36Z with the line `FAIL run(s) [42441204994] at this head are still being judged; their gate decides`. That is the edit/code deferral, superseded by the code run's gate, which classify reads green. The body's `## Red checks` answers this class ("the gate's edit/code deferral race, cleared by a later run") with job ids from the previous head's runs. Its admission that it could not show the deferral message is now settled by this log line, which also bears on the record's not-established deferral cause carried to #3156. `tests / nightly-status` is green at this head.
- Mutation proof: n/a, no production line changes. I re-ran no gate or mutation table (rule 11).
