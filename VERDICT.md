Fix review: merge 837f5f9d5bafe286236d519130a9c19ef92628b9

bus-nonce: 5e3c9c105498a354a6eb7f966c3bf7e2

Round 1 of a record PR (triage batch 114, ruling P372). Judged from a detached worktree at 837f5f9d5bafe286236d519130a9c19ef92628b9; head re-read before posting (ev/head-reread.txt).

## Findings

- Advisory, not blocking: the file's "Instances" bullet says #3158 is "open with REVIEW_REQUIRED"; at this head #3158 is also a draft (mergeable_state blocked). The delivery reading is unchanged (the carry waits on #3158 reaching main), so no ruling turns on it. Carry: dismissed: wording only; the ruling's premise (s6-batch110.md not on main) holds and the file already says delivery waits on that merge.
- Advisory, not blocking: the PR body says "the diff is one markdown file" while the three-dot diff holds two (the ruling and the PR's own delivery row). The ## Head section explains the row commit, so the body is accurate overall. Carry: dismissed: wording only, row is required by delivery-status-tracking.md.

## Evidence

- Diff scope: three-dot diff against merge base 279cb497f has exactly dev/programme/delivery/3172.md and dev/programme/triage/s6-batch114.md (+60/-0). No production code, VERSION, manifest, RELEASE_NOTES heading, claim file or golden changed (ev/claims.txt: 0 lines). merge-base equals origin/main, so no staleness. git merge-tree --write-tree origin/main head: rc 0, no conflict (ev/merge-tree.txt).
- Facts at origin/main 279cb497f, re-derived: review_packet.py line 594 is hot_file_refusals(touched, open_prs, boarded, 0) in handoff(); line 548 passes a.pr; line 215 is the p["number"] == this_pr skip. All as stated.
- Roster origin/handoff/audit-r10-roster is e431aee1a as stated. R10-ORCH-REVIEW-PACKET is present with carry 12, and P368 / b110-P368 appear nowhere in it, as the file says (carries land after the record merges, by design). The group's brief owns review_packet.py's packet. The roster's 'stage' field was not found as a literal key in the group record; the carry count and absence of P368 were verified, the stage string was not re-derived.
- #3065 head branch is fix/r10-fly-relay-review-ff-2 (read via the PR API); its body records the hot-file self-refusal (this_pr=0) as a Friction item, matching instance 1/2. #3085 head is fix/r10-closeout-cleanup, a different PR, as the file says. #3158 is open, titled triage: s9 batch 110, and its body states the carry text the file paraphrases: ancestry-first PR identification with branch-name fallback, ambiguity refusal, arms (a) own PR not refused, (b) null control, (c) ambiguity, mutant restoring 0 fails (a). The file's "stronger than the proposal" claim matches that text.
- Not re-derivable here: the seat ledger timestamps (01:54:39Z, 09:52:34Z) and roster-queue line 2199 live on the orchestrator's machine; the file's own cited instances are corroborated only by #3065's body (Friction) and #3158's body. s6-batch110.md is not on main, so P368's ACCEPT is read through #3158's body, not the tree.
- Ruling gate: roster_edit.ruling_verdict reads P372 as DEFER and P373 as None; with the verdict flipped to ACCEPT it reads ACCEPT; triage_refusal on a text citing s6-batch114.md#P372 is refused "is not an ACCEPT ruling (DEFER)", and with the file absent "the triage ruling ... is not on the roster branch or origin/main". Matches the body's mutation proof and null control. DEFER carries a stated, testable reason (owner exists; answer changes only if the group closes without the carry or the built rule still refuses own handoff).
- No quantified claim in the file other than the line numbers and the 12-carry count (checked above); no null control owed beyond the body's.
- Standing checks: ## Head names 837f5f9d5bafe286236d519130a9c19ef92628b9; ## Red checks says none, and the whole check-run set (43 runs, all pages) shows no concluded red at this head; delivery row present in the three-dot diff and lists #3172 open; no host path in added lines (grep for /home, /tmp, /Users empty); carry_audit at the head: 0 finding items, 0 unrouted; figure_lint 2 resolved, 1 unverified (a git show of a tool file, not a claim). Body Forward-carry: none, consistent with a DEFER that adds no carry.
- CI: merge_train classify exited 0 GREEN at 837f5f9d5bafe286236d519130a9c19ef92628b9 after WAIT polls (instrument-self-tests and prelude ran about 30 min); mutation, closures, fast, coverage, typing, policy-docs, delivery-status all success. No mutant owed: the diff writes no production line. Heavy runs cited, not re-run.
- Round 1.
