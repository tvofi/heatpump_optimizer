Fix review: merge 9fb03fc0241a95b2d5dfb72347346fc9a5e129c3

bus-nonce: a580eaccac6c2cb491bc29014be34431

Round 1, record PR, judged from a detached worktree at 9fb03fc0241a95b2d5dfb72347346fc9a5e129c3.

## Findings

- The ruling file and PR body call #3045 "open, approved at 9ef51b821". At review time #3045 is merged (merged_at 2026-11-01T14:39:44Z, as f48fb142c; its band is in origin/main's tests/ci_budgets.json, `critical_path_minutes_band` 1.3), though dev/programme/delivery/3045.md on main still reads "open". The ruling states its facts as read at df66556f2, so each statement was true when read, and its first reopening condition ("#3045 merges and main still goes red inside its band") now applies. A reader of P356 sees a DEFER to a merged PR. Carry: dismissed: the ruling dates its facts at df66556f2, its reopening condition 1 already covers the merged state, and the delivery row is the orchestrator's to flip at #3045's merge record

## Evidence

- Diff: three-dot against e4c9e2016 is two added files, dev/programme/triage/s6-batch100.md and dev/programme/delivery/3084.md (+99). No production code, tests, claim files, golden fixtures, VERSION, manifest or RELEASE_NOTES change. Delivery row present.
- Merge: `git merge-tree --write-tree origin/main` exits 0 (tree bfcdfd7b0), no conflicts.
- ## Head names 9fb03fc0241a95b2d5dfb72347346fc9a5e129c3. #3086 (1a8051350), which fixes the uutils-sleep red, is an ancestor of the head and of origin/main.
- CI: `merge_train.py classify` returned GREEN (rc 0). All 55 check-runs at this head are success or skipped (ev/check-runs.tsv); no concluded red at the head, so the ## Red checks answer for the earlier head's instrument-self-tests red is satisfied (main's red, cheapest detector named, fixed by #3086). Packet figure_lint: 4 resolved, 0 not verified. carry_audit: 0 findings routed.
- P355 figures: job 124777140994 conclusion success; steps Gather 06:52:07-06:52:38 (31 s), Fetch 06:52:38-06:52:46 (8 s), Grade 06:52:46-06:53:16 (30 s) all re-derived. The API gives job start 06:52:01 and end 06:53:18, i.e. 77 s, not the ruling's 74 s; the 3 s does not touch the 30 s overlap bound, so this is a nit not a finding. Workflow step lines 2291/2316/2321 and ci_ratchet.py lines 469/574 are exact at df66556f2 (they have since moved to 2296/2321/2326 and 488/593 on main). The job's `if` is push to main only; merge_train.py documents `--overlap` as making main_green log-only. A workflow edit forcing MODE: FULL follows from CLAUDE.md rule 1.
- P356 figures: band 1.3 and budget 34.267 confirmed in tests/ci_budgets.json; PUSH_WINDOW = 8. The 145-run 1.300 spread, the 59-run median 33.767 and sigma 1.638 are #3045's body figures; I did not re-derive them from the Actions history (not re-derived). The 16 h lag follows from 20 runs at about 29 runs a day, and the 5x jobs reads is 40 against 8 run job lists.
- No roster op is claimed and none is owed: neither ruling is an ACCEPT. Confirmed. Carries not being on the roster is by design for a triage batch.
- Mutation proof, null control: the body's proof concerns roster_edit.py's triage gate refusing non-ACCEPT rulings; I did not re-run it since the diff touches no code, and the file's verdict lines read REJECT and DEFER as stated.
